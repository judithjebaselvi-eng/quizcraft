from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from routes.auth import login_required, teacher_required
from models import db
from models.user import User
from models.test import Test, TestQuestion
from models.question import Question, QuestionOption
from models.attempt import Attempt, StudentAnswer
from models.evaluation import CustomField, CustomFieldValue
from datetime import datetime
import random

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/create', methods=['GET', 'POST'])
@teacher_required
def create_test():
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        
        name = request.form.get('name')
        subject = request.form.get('subject', 'General')
        
        test = Test(
            test_id=Test.generate_test_id(subject),
            teacher_id=user.id,
            name=name or 'Untitled Test',
            subject=subject,
            status='draft'
        )
        
        db.session.add(test)
        db.session.commit()
        
        return redirect(url_for('tests.edit_test', test_id=test.id))
    
    user = User.query.get(session['user_id'])
    return render_template('create_test.html', user=user)

@tests_bp.route('/test/<int:test_id>/add-question', methods=['POST'])
@teacher_required
def add_question_to_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        # Create question
        question = Question(
            question_text=data.get('question_text'),
            question_type=data.get('question_type', 'mcq'),
            subject=data.get('subject', test.subject),
            topic=data.get('topic', test.topic),
            difficulty=data.get('difficulty', test.difficulty)
        )
        db.session.add(question)
        db.session.flush()
        
        # Add options if MCQ
        if data.get('question_type') == 'mcq' and data.get('options'):
            for idx, option_text in enumerate(data.get('options')):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=option_text,
                    order=idx,
                    is_correct=(idx == data.get('correct_answer_index', 0))
                )
                db.session.add(option)
        
        # Add to test
        test_question = TestQuestion(
            test_id=test.id,
            question_id=question.id,
            order=len(test.questions),
            marks=data.get('marks', 1)
        )
        db.session.add(test_question)
        test.total_marks = (test.total_marks or 0) + int(data.get('marks', 1))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'question_id': question.id,
            'test_question_id': test_question.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/test/<int:test_id>/remove-question/<int:q_id>', methods=['POST'])
@teacher_required
def remove_question_from_test(test_id, q_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        test_question = TestQuestion.query.filter_by(test_id=test_id, question_id=q_id).first()
        if test_question:
            test.total_marks = max(0, (test.total_marks or 0) - test_question.marks)
            db.session.delete(test_question)
            db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/test/<test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    test = Test.query.filter_by(test_id=test_id).first_or_404()
    
    # Check if test is published
    if not test.is_published:
        return render_template('test_not_available.html', message='This test is not available'), 404
    
    # Check availability
    time_status = test.get_time_status()
    if time_status == 'not_started':
        return render_template('test_not_available.html', 
            message='This test has not started yet',
            start_time=test.start_datetime), 403
    elif time_status == 'ended':
        return render_template('test_not_available.html', 
            message='This test has ended'), 403
    
    if request.method == 'POST':
        # Start test attempt
        student_name = request.form.get('student_name')
        student_reg = request.form.get('student_registration_no')
        student_degree = request.form.get('student_degree')
        student_department = request.form.get('student_department')
        student_year = request.form.get('student_year')
        student_section = request.form.get('student_section')
        
        # Create attempt
        attempt = Attempt(
            test_id=test.id,
            student_id=session.get('user_id'),  # Could be None for anonymous
            student_name=student_name,
            student_registration_no=student_reg,
            student_degree=student_degree,
            student_department=student_department,
            student_year=student_year,
            student_section=student_section
        )
        
        db.session.add(attempt)
        db.session.flush()
        
        # Handle custom fields
        custom_fields = CustomField.query.filter_by(test_id=test.id).all()
        for field in custom_fields:
            value = request.form.get(f'field_{field.id}')
            if value:
                field_value = CustomFieldValue(
                    custom_field_id=field.id,
                    attempt_id=attempt.id,
                    field_value=value
                )
                db.session.add(field_value)
        
        db.session.commit()
        
        return redirect(url_for('tests.exam', attempt_id=attempt.attempt_id))
    
    # Get custom fields
    custom_fields = CustomField.query.filter_by(test_id=test.id).order_by(CustomField.order).all()
    
    return render_template('test_start.html',
        test=test,
        custom_fields=custom_fields
    )

@tests_bp.route('/exam/<attempt_id>')
def exam(attempt_id):
    attempt = Attempt.query.filter_by(attempt_id=attempt_id).first_or_404()
    test = attempt.test
    
    # Check if already submitted
    if attempt.is_submitted:
        return redirect(url_for('tests.result', attempt_id=attempt_id))
    
    # Check time restriction
    if not test.can_be_taken_now():
        return render_template('test_not_available.html', 
            message='Test is no longer available'), 403
    
    # Get questions
    questions = [tq.question for tq in test.questions]
    
    if test.randomize_questions:
        random.shuffle(questions)
    
    return render_template('exam.html',
        attempt=attempt,
        test=test,
        questions=questions
    )

@tests_bp.route('/api/attempt/<attempt_id>/submit', methods=['POST'])
def submit_attempt(attempt_id):
    attempt = Attempt.query.filter_by(attempt_id=attempt_id).first_or_404()
    test = attempt.test
    
    if attempt.is_submitted:
        return jsonify({'error': 'Test already submitted'}), 400
    
    data = request.get_json()
    answers = data.get('answers', {})
    
    try:
        # Check time restriction
        if not test.can_be_taken_now():
            return jsonify({'error': 'Test is no longer available'}), 403
        
        # Process answers
        correct = 0
        wrong = 0
        unanswered = 0
        total_score = 0.0
        
        for tq in test.questions:
            question = tq.question
            answer_key = f"q_{question.id}"
            
            student_answer = StudentAnswer(
                attempt_id=attempt.id,
                question_id=question.id
            )
            
            if answer_key in answers and answers[answer_key]:
                if question.question_type == 'mcq':
                    selected_option_id = answers[answer_key]
                    option = QuestionOption.query.get(selected_option_id)
                    if option:
                        student_answer.selected_option_id = selected_option_id
                        student_answer.answer_text = option.option_text
                        if option.is_correct:
                            student_answer.is_correct = True
                            correct += 1
                            total_score += tq.marks
                        else:
                            student_answer.is_correct = False
                            wrong += 1
                    else:
                        student_answer.is_correct = False
                        wrong += 1
                else:
                    student_answer.answer_text = answers[answer_key]
                    student_answer.is_correct = None  # Pending manual evaluation
                    unanswered += 1
                    attempt.evaluation_required = True
            else:
                student_answer.is_correct = False
                unanswered += 1
            
            db.session.add(student_answer)
        
        # Update attempt
        attempt.is_submitted = True
        attempt.submitted_at = datetime.utcnow()
        attempt.correct_count = correct
        attempt.wrong_count = wrong
        attempt.unanswered_count = unanswered
        attempt.score = total_score
        attempt.percentage = (total_score / test.total_marks * 100) if test.total_marks > 0 else 0
        
        # Calculate duration
        duration = (attempt.submitted_at - attempt.started_at).total_seconds()
        attempt.duration_seconds = int(duration)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'attempt_id': attempt.attempt_id,
            'score': attempt.score,
            'percentage': attempt.percentage
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tests_bp.route('/result/<attempt_id>')
def result(attempt_id):
    attempt = Attempt.query.filter_by(attempt_id=attempt_id).first_or_404()
    
    if not attempt.is_submitted:
        return redirect(url_for('tests.exam', attempt_id=attempt_id))
    
    return render_template('result.html', attempt=attempt)
