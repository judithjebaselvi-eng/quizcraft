from models import db
from datetime import datetime
import uuid

class Attempt(db.Model):
    __tablename__ = 'attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Student information
    student_name = db.Column(db.String(200), nullable=False)
    student_registration_no = db.Column(db.String(50))
    student_degree = db.Column(db.String(100))
    student_department = db.Column(db.String(100))
    student_year = db.Column(db.String(50))
    student_section = db.Column(db.String(50))
    
    # Attempt tracking
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    is_submitted = db.Column(db.Boolean, default=False)
    duration_seconds = db.Column(db.Integer)  # How long it took
    
    # Results
    correct_count = db.Column(db.Integer, default=0)
    wrong_count = db.Column(db.Integer, default=0)
    unanswered_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    
    # Evaluation status
    evaluation_required = db.Column(db.Boolean, default=False)  # For manual evaluation
    is_evaluated = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_answers = db.relationship('StudentAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')
    evaluation = db.relationship('Evaluation', backref='attempt', uselist=False, cascade='all, delete-orphan')
    custom_field_values = db.relationship('CustomFieldValue', backref='attempt', lazy=True, cascade='all, delete-orphan')
    
    def get_duration_display(self):
        """Get formatted duration"""
        if not self.duration_seconds:
            return "N/A"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}m {seconds}s"
    
    def to_dict(self, include_answers=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'test_id': self.test_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'student_registration_no': self.student_registration_no,
            'student_degree': self.student_degree,
            'student_department': self.student_department,
            'student_year': self.student_year,
            'student_section': self.student_section,
            'started_at': self.started_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'is_submitted': self.is_submitted,
            'duration_seconds': self.duration_seconds,
            'duration_display': self.get_duration_display(),
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'unanswered_count': self.unanswered_count,
            'score': self.score,
            'percentage': self.percentage,
            'evaluation_required': self.evaluation_required,
            'is_evaluated': self.is_evaluated,
            'created_at': self.created_at.isoformat()
        }
        if include_answers:
            data['answers'] = [ans.to_dict() for ans in self.student_answers]
        return data

class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text)  # For text-based answers
    selected_option_id = db.Column(db.Integer)  # For MCQ/multiple select
    is_correct = db.Column(db.Boolean)  # NULL if unanswered or pending evaluation
    marks_obtained = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'selected_option_id': self.selected_option_id,
            'is_correct': self.is_correct,
            'marks_obtained': self.marks_obtained,
            'created_at': self.created_at.isoformat()
        }
