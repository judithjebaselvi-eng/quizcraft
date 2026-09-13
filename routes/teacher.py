from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from routes.auth import teacher_required, login_required
from models import db
from models.user import User
from models.teacher import TeacherProfile
from models.test import Test
from models.attempt import Attempt
from datetime import datetime
import json

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    user = User.query.get(session['user_id'])
    teacher_profile = user.teacher_profile
    
    # Get test statistics
    all_tests = Test.query.filter_by(teacher_id=user.id).all()
    total_tests = len(all_tests)
    published_tests = len([t for t in all_tests if t.is_published])
    draft_tests = len([t for t in all_tests if not t.is_published])
    
    # Get attempts
    all_attempts = Attempt.query.join(Test).filter(
        Test.teacher_id == user.id
    ).all()
    total_attempts = len(all_attempts)
    
    # Calculate average score
    if all_attempts:
        average_score = sum([a.percentage for a in all_attempts if a.is_submitted]) / len([a for a in all_attempts if a.is_submitted]) if [a for a in all_attempts if a.is_submitted] else 0
    else:
        average_score = 0
    
    # Get recent tests (limit to 5)
    recent_tests = sorted(all_tests, key=lambda x: x.created_at, reverse=True)[:5]
    
    return render_template('teacher_dashboard.html',
        teacher=user,
        profile=teacher_profile,
        total_tests=total_tests,
        published_tests=published_tests,
        draft_tests=draft_tests,
        total_attempts=total_attempts,
        average_score=average_score,
        recent_tests=recent_tests
    )

@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
def profile():
    user = User.query.get(session['user_id'])
    teacher_profile = user.teacher_profile
    
    if request.method == 'POST':
        teacher_profile.degree = request.form.get('degree')
        teacher_profile.department = request.form.get('department')
        teacher_profile.year = request.form.get('year')
        teacher_profile.section = request.form.get('section')
        teacher_profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': teacher_profile.to_dict()
        }), 200
    
    return render_template('teacher_profile.html',
        user=user,
        profile=teacher_profile
    )

@teacher_bp.route('/tests')
@teacher_required
def my_tests():
    user = User.query.get(session['user_id'])
    tests = Test.query.filter_by(teacher_id=user.id).order_by(Test.created_at.desc()).all()
    
    return render_template('my_tests.html',
        user=user,
        tests=tests
    )

@teacher_bp.route('/test/<int:test_id>')
@teacher_required
def view_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    # Check ownership
    if test.teacher_id != user.id:
        return redirect(url_for('teacher.dashboard')), 403
    
    return render_template('view_test.html',
        test=test,
        user=user
    )

@teacher_bp.route('/test/<int:test_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return redirect(url_for('teacher.dashboard')), 403
    
    if request.method == 'POST':
        # Update test details
        test.name = request.form.get('name')
        test.description = request.form.get('description')
        test.subject = request.form.get('subject')
        test.topic = request.form.get('topic')
        test.lesson = request.form.get('lesson')
        test.degree = request.form.get('degree')
        test.department = request.form.get('department')
        test.year = request.form.get('year')
        test.section = request.form.get('section')
        test.difficulty = request.form.get('difficulty')
        test.instructions = request.form.get('instructions')
        test.max_attempts = int(request.form.get('max_attempts', 1))
        test.auto_submit = request.form.get('auto_submit') == 'on'
        test.immediate_results = request.form.get('immediate_results') == 'on'
        test.manual_evaluation = request.form.get('manual_evaluation') == 'on'
        test.randomize_questions = request.form.get('randomize_questions') == 'on'
        test.randomize_options = request.form.get('randomize_options') == 'on'
        
        # Handle availability
        test.availability_enabled = request.form.get('availability_enabled') == 'on'
        if test.availability_enabled:
            start_date = request.form.get('start_date')
            start_time = request.form.get('start_time')
            end_date = request.form.get('end_date')
            end_time = request.form.get('end_time')
            
            if start_date and start_time:
                test.start_datetime = datetime.fromisoformat(f"{start_date}T{start_time}")
            if end_date and end_time:
                test.end_datetime = datetime.fromisoformat(f"{end_date}T{end_time}")
        
        # Handle duration
        test.duration_enabled = request.form.get('duration_enabled') == 'on'
        if test.duration_enabled:
            test.duration_minutes = int(request.form.get('duration_minutes', 0))
        
        test.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test updated successfully',
            'test': test.to_dict()
        }), 200
    
    return render_template('edit_test.html',
        test=test,
        user=user
    )

@teacher_bp.route('/test/<int:test_id>/delete', methods=['POST'])
@teacher_required
def delete_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(test)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Test deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete test'}), 500

@teacher_bp.route('/test/<int:test_id>/publish', methods=['POST'])
@teacher_required
def publish_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not test.questions or len(test.questions) == 0:
        return jsonify({'error': 'Cannot publish test without questions'}), 400
    
    test.is_published = True
    test.status = 'published'
    test.published_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Test published successfully',
        'test_id': test.test_id,
        'share_url': f"/test/{test.test_id}"
    }), 200

@teacher_bp.route('/test/<int:test_id>/duplicate', methods=['POST'])
@teacher_required
def duplicate_test(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create new test
        new_test = Test(
            test_id=Test.generate_test_id(test.subject),
            teacher_id=user.id,
            name=f"{test.name} (Copy)",
            description=test.description,
            subject=test.subject,
            topic=test.topic,
            lesson=test.lesson,
            degree=test.degree,
            department=test.department,
            year=test.year,
            section=test.section,
            difficulty=test.difficulty,
            total_marks=test.total_marks,
            duration_minutes=test.duration_minutes,
            duration_enabled=test.duration_enabled,
            instructions=test.instructions,
            max_attempts=test.max_attempts,
            auto_submit=test.auto_submit,
            immediate_results=test.immediate_results,
            manual_evaluation=test.manual_evaluation,
            randomize_questions=test.randomize_questions,
            randomize_options=test.randomize_options,
            status='draft'
        )
        db.session.add(new_test)
        db.session.flush()
        
        # Copy questions
        from models.test import TestQuestion
        for tq in test.questions:
            new_tq = TestQuestion(
                test_id=new_test.id,
                question_id=tq.question_id,
                order=tq.order,
                marks=tq.marks
            )
            db.session.add(new_tq)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test duplicated successfully',
            'new_test_id': new_test.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to duplicate test'}), 500
