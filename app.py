import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db
from models.user import User
from models.teacher import TeacherProfile
from models.test import Test
from models.attempt import Attempt
from datetime import timedelta
from functools import wraps

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database
db.init_app(app)

# Import routes
from routes import auth, teacher, student, tests, results, ai

# Register blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(teacher.teacher_bp)
app.register_blueprint(student.student_bp)
app.register_blueprint(tests.tests_bp)
app.register_blueprint(results.results_bp)
app.register_blueprint(ai.ai_bp)

# Middleware to set session timeout
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)
    session.modified = True

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            if user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        print("✓ Database initialized")
        
        # Create demo teacher account if it doesn't exist
        demo_teacher = User.query.filter_by(username='teacher_demo').first()
        if not demo_teacher:
            demo_teacher = User(
                username='teacher_demo',
                email='teacher@quizcraft.com',
                full_name='Demo Teacher',
                role='teacher'
            )
            demo_teacher.set_password('password123')
            db.session.add(demo_teacher)
            db.session.commit()
            
            # Create teacher profile
            profile = TeacherProfile(
                user_id=demo_teacher.id,
                degree='B.Tech',
                department='Information Technology',
                year='3rd Year',
                section='A'
            )
            db.session.add(profile)
            db.session.commit()
            print("✓ Demo teacher account created")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
