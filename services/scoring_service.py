class ScoringService:
    """Handle test scoring and result calculations"""
    
    @staticmethod
    def calculate_score(attempt):
        """
        Calculate final score and percentage for an attempt.
        Backend-only calculation - never trust frontend values.
        """
        if not attempt or not attempt.test:
            return 0, 0
        
        total_marks = attempt.test.total_marks or 0
        if total_marks == 0:
            return 0, 0
        
        # Calculate actual score from submitted answers
        from models.attempt import StudentAnswer
        answers = StudentAnswer.query.filter_by(attempt_id=attempt.id).all()
        
        score = 0
        correct = 0
        wrong = 0
        unanswered = 0
        
        for answer in answers:
            if answer.is_correct is None:
                # Pending manual evaluation
                unanswered += 1
            elif answer.is_correct:
                correct += 1
                # Add marks if available
                if answer.marks_obtained:
                    score += answer.marks_obtained
                else:
                    # Find the corresponding TestQuestion for marks
                    from models.test import TestQuestion
                    tq = TestQuestion.query.filter_by(
                        test_id=attempt.test_id,
                        question_id=answer.question_id
                    ).first()
                    if tq:
                        score += tq.marks
                        answer.marks_obtained = tq.marks
            else:
                wrong += 1
        
        percentage = (score / total_marks * 100) if total_marks > 0 else 0
        
        return score, percentage
    
    @staticmethod
    def get_celebration_level(percentage):
        """
        Determine celebration animation level based on percentage.
        No Pass/Fail - only celebration levels.
        """
        if percentage >= 90:
            return {
                'level': 'excellent',
                'message': 'CONGRATULATIONS! 🎉',
                'subtitle': 'Excellent! Perfect or near-perfect score!',
                'confetti': True,
                'emoji': '🎉'
            }
        elif percentage >= 80:
            return {
                'level': 'great',
                'message': 'Great Job! 🌟',
                'subtitle': 'Outstanding performance!',
                'confetti': True,
                'emoji': '🌟'
            }
        elif percentage >= 70:
            return {
                'level': 'good',
                'message': 'Good Work! 👏',
                'subtitle': 'Keep practicing to improve further!',
                'confetti': False,
                'emoji': '👏'
            }
        else:
            return {
                'level': 'normal',
                'message': 'Keep Practicing! 💪',
                'subtitle': 'You can do better! Review the concepts and try again.',
                'confetti': False,
                'emoji': '💪'
            }
    
    @staticmethod
    def validate_score_integrity(attempt):
        """
        Validate that score hasn't been tampered with.
        Compare calculated score with stored score.
        """
        calculated_score, calculated_percentage = ScoringService.calculate_score(attempt)
        
        # Allow small tolerance due to rounding
        tolerance = 0.01
        
        score_valid = abs(attempt.score - calculated_score) <= tolerance
        percentage_valid = abs(attempt.percentage - calculated_percentage) <= tolerance
        
        return score_valid and percentage_valid
