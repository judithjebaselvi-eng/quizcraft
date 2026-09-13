from models import db
from datetime import datetime

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Teacher who evaluated
    evaluation_type = db.Column(db.String(50))  # 'auto' or 'manual'
    feedback = db.Column(db.Text)  # Overall feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'evaluator_id': self.evaluator_id,
            'evaluation_type': self.evaluation_type,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CustomField(db.Model):
    __tablename__ = 'custom_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)  # e.g., 'Class', 'Batch', 'Email'
    field_type = db.Column(db.String(50), default='text')  # text, email, number
    is_required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    field_values = db.relationship('CustomFieldValue', backref='field', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'field_name': self.field_name,
            'field_type': self.field_type,
            'is_required': self.is_required,
            'order': self.order
        }

class CustomFieldValue(db.Model):
    __tablename__ = 'custom_field_values'
    
    id = db.Column(db.Integer, primary_key=True)
    custom_field_id = db.Column(db.Integer, db.ForeignKey('custom_fields.id'), nullable=False)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    field_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'custom_field_id': self.custom_field_id,
            'attempt_id': self.attempt_id,
            'field_value': self.field_value,
            'field_name': self.field.field_name if self.field else None
        }
