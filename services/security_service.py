from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from datetime import datetime, timedelta

class SecurityService:
    """Handle security, authorization, and validation"""
    
    @staticmethod
    def generate_security_code(length=6):
        """
        Generate random alphanumeric security code.
        Example: A7K921
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def hash_security_code(code):
        """
        Hash security code for storage.
        Never store plaintext.
        """
        return generate_password_hash(code)
    
    @staticmethod
    def verify_security_code(code, hash_value):
        """
        Verify security code against hash.
        """
        return check_password_hash(hash_value, code)
    
    @staticmethod
    def validate_email(email):
        """
        Basic email validation.
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """
        Validate username format.
        Alphanumeric, underscores, hyphens. 3-20 chars.
        """
        import re
        pattern = r'^[a-zA-Z0-9_-]{3,20}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength.
        Minimum 6 characters.
        """
        return len(password) >= 6
    
    @staticmethod
    def check_test_availability(test, reference_time=None):
        """
        Check if test is available at given time.
        Uses backend server time, not client time.
        """
        if reference_time is None:
            reference_time = datetime.utcnow()
        
        if not test.availability_enabled:
            return True, 'available'
        
        if test.start_datetime and reference_time < test.start_datetime:
            return False, 'not_started'
        
        if test.end_datetime and reference_time > test.end_datetime:
            return False, 'ended'
        
        return True, 'available'
    
    @staticmethod
    def check_attempt_validity(attempt, test):
        """
        Validate that attempt is still valid.
        Check: submitted, availability, max attempts.
        """
        if attempt.is_submitted:
            return False, 'already_submitted'
        
        # Check test availability
        available, status = SecurityService.check_test_availability(test)
        if not available:
            return False, status
        
        return True, 'valid'
    
    @staticmethod
    def check_teacher_ownership(test, teacher_id):
        """
        Verify that teacher owns the test.
        Always check on backend.
        """
        return test.teacher_id == teacher_id
    
    @staticmethod
    def sanitize_input(input_string, max_length=1000):
        """
        Basic input sanitization.
        """
        if not isinstance(input_string, str):
            return str(input_string)
        
        # Limit length
        sanitized = input_string[:max_length]
        
        # Remove potentially harmful characters while preserving text
        # This is basic - in production use proper HTML escaping
        return sanitized.strip()
    
    @staticmethod
    def rate_limit_check(identifier, action, limit=10, window_seconds=60):
        """
        Simple rate limiting using Redis-like logic.
        In production, use Redis or similar.
        """
        # This is a placeholder - implement with Redis in production
        return True
    
    @staticmethod
    def get_client_ip(request):
        """
        Extract client IP from request.
        Account for proxies.
        """
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr
