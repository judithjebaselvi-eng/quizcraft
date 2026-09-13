from models import db
from datetime import datetime
import uuid
import secrets
import string

class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # QC-SUBJECT-XXXX
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100))
    lesson = db.Column(db.String(100))
    degree = db.Column(db.String(100))
    department = db.Column(db.String(100))
    year = db.Column(db.String(50))
    section = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    total_marks = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer)  # NULL if no duration
    duration_enabled = db.Column(db.Boolean, default=False)
    instructions = db.Column(db.Text)
    
    # Settings
    max_attempts = db.Column(db.Integer, default=1)
    auto_submit = db.Column(db.Boolean, default=False)
    immediate_results = db.Column(db.Boolean, default=True)
    manual_evaluation = db.Column(db.Boolean, default=False)
    randomize_questions = db.Column(db.Boolean, default=False)
    randomize_options = db.Column(db.Boolean, default=False)
    
    # Time restrictions
    availability_enabled = db.Column(db.Boolean, default=False)
    start_datetime = db.Column(db.DateTime)  # NULL if no start time
    end_datetime = db.Column(db.DateTime)  # NULL if no end time
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, published, closed, archived
    is_published = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    questions = db.relationship('TestQuestion', backref='test', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('Attempt', backref='test', lazy=True, cascade='all, delete-orphan')
    custom_fields = db.relationship('CustomField', backref='test', lazy=True, cascade='all, delete-orphan')
    
    @staticmethod
    def generate_test_id(subject):
        """Generate unique test ID like QC-SUBJECT-XXXX"""
        subject_abbr = ''.join([c for c in subject.upper() if c.isalpha()])[:4]
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
        return f"QC-{subject_abbr}-{random_suffix}"
    
    def get_question_count(self):
        """Get total questions in test"""
        return len(self.questions)
    
    def can_be_taken_now(self):
        """Check if test can be taken at current time"""
        if not self.availability_enabled:
            return True
        now = datetime.utcnow()
        if self.start_datetime and now < self.start_datetime:
            return False
        if self.end_datetime and now > self.end_datetime:
            return False
        return True
    
    def get_time_status(self):
        """Get test time status"""
        if not self.availability_enabled:
            return "no_restriction"
        now = datetime.utcnow()
        if self.start_datetime and now < self.start_datetime:
            return "not_started"
        if self.end_datetime and now > self.end_datetime:
            return "ended"
        return "active"
    
    def to_dict(self, include_questions=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'test_id': self.test_id,
            'name': self.name,
            'description': self.description,
            'subject': self.subject,
            'topic': self.topic,
            'lesson': self.lesson,
            'degree': self.degree,
            'department': self.department,
            'year': self.year,
            'section': self.section,
            'difficulty': self.difficulty,
            'total_marks': self.total_marks,
            'duration_minutes': self.duration_minutes,
            'duration_enabled': self.duration_enabled,
            'instructions': self.instructions,
            'max_attempts': self.max_attempts,
            'auto_submit': self.auto_submit,
            'immediate_results': self.immediate_results,
            'manual_evaluation': self.manual_evaluation,
            'randomize_questions': self.randomize_questions,
            'randomize_options': self.randomize_options,
            'availability_enabled': self.availability_enabled,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'is_published': self.is_published,
            'question_count': self.get_question_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
        if include_questions:
            data['questions'] = [q.to_dict() for q in self.questions]
        return data

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='test_instances')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'test_id': self.test_id,
            'question': self.question.to_dict(),
            'order': self.order,
            'marks': self.marks
        }
