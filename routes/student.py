from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from routes.auth import login_required, student_required
from models import db
from models.user import User
from models.test import Test
from models.attempt import Attempt
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Get student's attempts
    attempts = Attempt.query.filter_by(student_id=user.id).order_by(Attempt.created_at.desc()).all()
    
    return render_template('student_dashboard.html',
        user=user,
        attempts=attempts
    )
