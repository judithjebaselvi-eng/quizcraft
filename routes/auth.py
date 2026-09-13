from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from models import db
from models.user import User
from models.teacher import TeacherProfile
from functools import wraps
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'teacher':
            return redirect(url_for('auth.login')), 403
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'student':
            return redirect(url_for('auth.login')), 403
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if not username_or_email or not password:
            return render_template('login.html', error='Email/Username and password are required'), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            session.permanent = True if remember_me else False
            
            if user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            return render_template('login.html', error='Invalid email/username or password'), 401
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validation
        errors = []
        if not all([full_name, username, email, password, confirm_password, role]):
            errors.append('All fields are required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if role not in ['student', 'teacher']:
            errors.append('Invalid role selected')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            return render_template('register.html', errors=errors), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.flush()
            
            # If teacher, create empty profile
            if role == 'teacher':
                profile = TeacherProfile(user_id=user.id)
                db.session.add(profile)
            
            db.session.commit()
            
            return render_template('register.html', success=True, username=username), 200
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', errors=['Registration failed. Please try again.']), 500
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/me')
def get_user():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user': user.to_dict()
    }), 200
