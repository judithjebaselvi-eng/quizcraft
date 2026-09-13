from flask import Blueprint, render_template, request, jsonify, session
from routes.auth import teacher_required
from models import db
from models.user import User
from models.question import Question, QuestionOption
from services.ai_service import AIService
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

ai_service = AIService()

@ai_bp.route('/generate', methods=['POST'])
@teacher_required
def generate_questions():
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        questions = ai_service.generate_questions(prompt)
        return jsonify({
            'success': True,
            'questions': questions
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate questions',
            'details': str(e)
        }), 500

@ai_bp.route('/save-questions', methods=['POST'])
@teacher_required
def save_generated_questions():
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    test_id = data.get('test_id')
    questions_data = data.get('questions', [])
    
    if not test_id or not questions_data:
        return jsonify({'error': 'Invalid data'}), 400
    
    try:
        from models.test import TestQuestion
        from models.test import Test
        
        test = Test.query.get_or_404(test_id)
        if test.teacher_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        question_ids = []
        total_marks = 0
        
        for q_data in questions_data:
            question = Question(
                question_text=q_data.get('question_text'),
                question_type=q_data.get('question_type', 'mcq'),
                subject=q_data.get('subject', test.subject),
                topic=q_data.get('topic', test.topic),
                difficulty=q_data.get('difficulty', 'medium')
            )
            db.session.add(question)
            db.session.flush()
            
            # Add options
            if q_data.get('options'):
                for idx, option_text in enumerate(q_data.get('options')):
                    option = QuestionOption(
                        question_id=question.id,
                        option_text=option_text,
                        order=idx,
                        is_correct=(idx == q_data.get('correct_answer_index', 0))
                    )
                    db.session.add(option)
            
            # Add to test
            marks = int(q_data.get('marks', 1))
            test_question = TestQuestion(
                test_id=test.id,
                question_id=question.id,
                order=len(test.questions),
                marks=marks
            )
            db.session.add(test_question)
            
            question_ids.append(question.id)
            total_marks += marks
        
        test.total_marks = (test.total_marks or 0) + total_marks
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(question_ids)} questions added',
            'question_ids': question_ids,
            'total_marks': test.total_marks
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
