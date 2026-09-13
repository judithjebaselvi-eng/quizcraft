from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from routes.auth import teacher_required
from models import db
from models.user import User
from models.test import Test
from models.attempt import Attempt
from models.evaluation import Evaluation
from datetime import datetime

results_bp = Blueprint('results', __name__, url_prefix='/results')

@results_bp.route('/test/<int:test_id>')
@teacher_required
def test_results(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return redirect(url_for('teacher.dashboard')), 403
    
    attempts = Attempt.query.filter_by(test_id=test_id, is_submitted=True).order_by(Attempt.submitted_at.desc()).all()
    
    return render_template('test_results.html',
        test=test,
        user=user,
        attempts=attempts
    )

@results_bp.route('/attempt/<attempt_id>')
@teacher_required
def view_attempt(attempt_id):
    attempt = Attempt.query.filter_by(attempt_id=attempt_id).first_or_404()
    test = attempt.test
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return redirect(url_for('teacher.dashboard')), 403
    
    return render_template('attempt_detail.html',
        attempt=attempt,
        test=test,
        user=user
    )

@results_bp.route('/analytics/<int:test_id>')
@teacher_required
def test_analytics(test_id):
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return redirect(url_for('teacher.dashboard')), 403
    
    attempts = Attempt.query.filter_by(test_id=test_id, is_submitted=True).all()
    
    # Calculate statistics
    if attempts:
        percentages = [a.percentage for a in attempts]
        average = sum(percentages) / len(percentages)
        highest = max(percentages)
        lowest = min(percentages)
    else:
        average = highest = lowest = 0
    
    return render_template('test_analytics.html',
        test=test,
        user=user,
        attempts=attempts,
        average=average,
        highest=highest,
        lowest=lowest,
        total_attempts=len(attempts)
    )

@results_bp.route('/api/attempt/<attempt_id>/evaluate', methods=['POST'])
@teacher_required
def evaluate_attempt(attempt_id):
    attempt = Attempt.query.filter_by(attempt_id=attempt_id).first_or_404()
    test = attempt.test
    user = User.query.get(session['user_id'])
    
    if test.teacher_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        # Update answer marks
        for answer_id, marks in data.get('marks_update', {}).items():
            answer = StudentAnswer.query.get(answer_id)
            if answer and answer.attempt_id == attempt.id:
                answer.marks_obtained = float(marks)
                answer.is_correct = float(marks) > 0
        
        # Recalculate score
        from models.attempt import StudentAnswer
        all_answers = StudentAnswer.query.filter_by(attempt_id=attempt.id).all()
        total_score = sum([a.marks_obtained for a in all_answers])
        attempt.score = total_score
        attempt.percentage = (total_score / test.total_marks * 100) if test.total_marks > 0 else 0
        attempt.is_evaluated = True
        
        # Create evaluation record
        evaluation = Evaluation.query.filter_by(attempt_id=attempt.id).first()
        if not evaluation:
            evaluation = Evaluation(
                attempt_id=attempt.id,
                evaluator_id=user.id,
                evaluation_type='manual'
            )
            db.session.add(evaluation)
        else:
            evaluation.updated_at = datetime.utcnow()
        
        evaluation.feedback = data.get('feedback', '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evaluation saved',
            'score': attempt.score,
            'percentage': attempt.percentage
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
