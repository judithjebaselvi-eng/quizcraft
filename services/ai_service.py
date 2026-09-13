import os
import requests
import json
from typing import List, Dict
import random

class AIService:
    """Handle AI-powered question generation"""
    
    DEMO_QUESTIONS = {
        'chemistry': [
            {
                'question_text': 'What is the atomic number of Oxygen?',
                'question_type': 'mcq',
                'options': ['6', '7', '8', '9'],
                'correct_answer_index': 2,
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'The process by which atoms combine to form molecules is called __________.',
                'question_type': 'fill_blanks',
                'difficulty': 'medium',
                'marks': 1
            },
            {
                'question_text': 'Valence electrons are electrons in the outermost shell of an atom. True or False?',
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            }
        ],
        'dbms': [
            {
                'question_text': 'What does DBMS stand for?',
                'question_type': 'mcq',
                'options': ['Database Management System', 'Digital Business Management Software', 'Dynamic Base Management System', 'Database Module Software'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'Normalization helps to reduce __________.',
                'question_type': 'fill_blanks',
                'difficulty': 'medium',
                'marks': 1
            },
            {
                'question_text': 'A primary key can contain NULL values. True or False?',
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer_index': 1,
                'difficulty': 'easy',
                'marks': 1
            }
        ],
        'python': [
            {
                'question_text': 'Which of the following is a correct way to create a list in Python?',
                'question_type': 'mcq',
                'options': ['list = [1, 2, 3]', 'list = (1, 2, 3)', 'list = {1, 2, 3}', 'list = 1, 2, 3'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'The __________ function in Python returns the length of an object.',
                'question_type': 'fill_blanks',
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'Python is an interpreted language. True or False?',
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            }
        ],
        'physics': [
            {
                'question_text': 'What is the SI unit of force?',
                'question_type': 'mcq',
                'options': ['Joule', 'Newton', 'Pascal', 'Watt'],
                'correct_answer_index': 1,
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'The speed of light in vacuum is approximately __________ m/s.',
                'question_type': 'fill_blanks',
                'difficulty': 'medium',
                'marks': 1
            },
            {
                'question_text': 'Acceleration is the rate of change of velocity. True or False?',
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            }
        ],
        'mathematics': [
            {
                'question_text': 'What is the derivative of x^2?',
                'question_type': 'mcq',
                'options': ['x', '2x', 'x^2', '2x^2'],
                'correct_answer_index': 1,
                'difficulty': 'medium',
                'marks': 1
            },
            {
                'question_text': 'The value of π is approximately __________.',
                'question_type': 'fill_blanks',
                'difficulty': 'easy',
                'marks': 1
            },
            {
                'question_text': 'The sum of angles in a triangle is 180 degrees. True or False?',
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer_index': 0,
                'difficulty': 'easy',
                'marks': 1
            }
        ]
    }
    
    def __init__(self):
        self.api_key = os.getenv('AI_API_KEY')
        self.api_url = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
        self.model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    def generate_questions(self, prompt: str) -> List[Dict]:
        """
        Generate questions using AI API or fallback to demo mode
        """
        
        # Try to use real AI API if configured
        if self.api_key and self.api_key != 'your_ai_api_key_here':
            try:
                return self._generate_with_api(prompt)
            except Exception as e:
                print(f"AI API failed: {e}. Using demo mode...")
        
        # Fallback to demo AI mode
        return self._generate_demo_questions(prompt)
    
    def _generate_with_api(self, prompt: str) -> List[Dict]:
        """
        Generate questions using actual AI API (OpenAI)
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        system_prompt = """You are an expert educational test creator. Generate quiz questions based on the user's request.
        Return a JSON array of questions with the following structure for each question:
        {
            "question_text": "The question",
            "question_type": "mcq|fill_blanks|true_false|short_answer|long_answer",
            "difficulty": "easy|medium|hard",
            "marks": 1,
            "options": ["option1", "option2", ...] (for MCQ, true/false),
            "correct_answer_index": 0 (for MCQ)
        }
        Ensure the JSON is valid and properly formatted."""
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse JSON from response
        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            questions = json.loads(content.strip())
            return questions if isinstance(questions, list) else [questions]
        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to demo
            return self._generate_demo_questions(prompt)
    
    def _generate_demo_questions(self, prompt: str) -> List[Dict]:
        """
        Generate demo questions based on subject/topic from prompt
        """
        prompt_lower = prompt.lower()
        
        # Detect subject from prompt
        subject_key = 'mathematics'  # default
        
        if any(word in prompt_lower for word in ['chemistry', 'atom', 'molecule', 'chemical']):
            subject_key = 'chemistry'
        elif any(word in prompt_lower for word in ['dbms', 'database', 'sql', 'normalization']):
            subject_key = 'dbms'
        elif any(word in prompt_lower for word in ['python', 'programming', 'code']):
            subject_key = 'python'
        elif any(word in prompt_lower for word in ['physics', 'force', 'motion', 'energy']):
            subject_key = 'physics'
        elif any(word in prompt_lower for word in ['math', 'calculus', 'algebra', 'geometry']):
            subject_key = 'mathematics'
        
        # Get demo questions for subject
        questions = self.DEMO_QUESTIONS.get(subject_key, self.DEMO_QUESTIONS['mathematics'])
        
        # Make a copy and slightly vary
        result = []
        for q in questions:
            q_copy = q.copy()
            if 'options' in q_copy and q_copy['question_type'] == 'mcq':
                # Shuffle options
                options = q_copy['options'].copy()
                correct = options[q_copy['correct_answer_index']]
                random.shuffle(options)
                q_copy['options'] = options
                q_copy['correct_answer_index'] = options.index(correct)
            result.append(q_copy)
        
        return result
