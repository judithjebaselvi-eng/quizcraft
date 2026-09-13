from models import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # mcq, multiple_select, true_false, fill_blanks, one_word, short_answer, long_answer, match_following, coding
    subject = db.Column(db.String(100))
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('QuestionOption', backref='question', lazy=True, cascade='all, delete-orphan')
    answers = db.relationship('StudentAnswer', backref='question', lazy=True, cascade='all, delete-orphan')
    correct_answer = db.relationship('QuestionOption', uselist=False, foreign_keys=[id])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'subject': self.subject,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'options': [opt.to_dict() for opt in self.options],
            'created_at': self.created_at.isoformat()
        }

class QuestionOption(db.Model):
    __tablename__ = 'question_options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'option_text': self.option_text,
            'order': self.order,
            'is_correct': self.is_correct
        }
