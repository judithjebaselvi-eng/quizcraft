from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.teacher import TeacherProfile
from models.test import Test, TestQuestion
from models.question import Question, QuestionOption
from models.attempt import Attempt, StudentAnswer
from models.evaluation import Evaluation, CustomField, CustomFieldValue

__all__ = [
    'db',
    'User',
    'TeacherProfile',
    'Test',
    'TestQuestion',
    'Question',
    'QuestionOption',
    'Attempt',
    'StudentAnswer',
    'Evaluation',
    'CustomField',
    'CustomFieldValue'
]
