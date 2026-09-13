from models import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class TeacherProfile(db.Model):
    __tablename__ = 'teacher_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    degree = db.Column(db.String(100))  # B.Tech, M.Tech, etc.
    department = db.Column(db.String(100))  # Information Technology, etc.
    year = db.Column(db.String(50))  # 1st Year, 2nd Year, etc.
    section = db.Column(db.String(50))  # A, B, C, etc.
    security_code_hash = db.Column(db.String(255))  # Hashed 6-char code
    security_code_verified = db.Column(db.Boolean, default=False)
    last_verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_security_code(self, code):
        """Hash and set security code"""
        self.security_code_hash = generate_password_hash(code)
    
    def check_security_code(self, code):
        """Check if provided code matches hash"""
        return check_password_hash(self.security_code_hash, code)
    
    def get_display_profile(self):
        """Get formatted profile display"""
        parts = []
        if self.degree:
            parts.append(self.degree)
        if self.department:
            parts.append(self.department)
        if self.year:
            parts.append(self.year)
        if self.section:
            parts.append(f"Section {self.section}")
        return " • ".join(parts) if parts else "No profile set"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'degree': self.degree,
            'department': self.department,
            'year': self.year,
            'section': self.section,
            'display_profile': self.get_display_profile(),
            'security_code_verified': self.security_code_verified
        }
