import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Student profile fields
    education_level = db.Column(db.String(80), default='Undergraduate')  # High School, Undergraduate, Graduate
    degree_specialization = db.Column(db.String(150), default='B.Tech in Computer Science')
    current_year = db.Column(db.String(50), default='3rd Year')
    technical_skills = db.Column(db.Text, default='Python, SQL, HTML, CSS')  # Comma-separated or JSON string
    programming_languages = db.Column(db.Text, default='Python, JavaScript')
    interests = db.Column(db.Text, default='Machine Learning, Web Development')
    certifications = db.Column(db.Text, default='')
    projects = db.Column(db.Text, default='')
    preferred_role = db.Column(db.String(100), default='Machine Learning Engineer')
    career_goals = db.Column(db.Text, default='Secure a competitive AI/ML role or internship')
    experience_level = db.Column(db.String(50), default='Intermediate')  # Beginner, Intermediate, Advanced
    
    # Relationships
    assessments = db.relationship('AssessmentResult', backref='user', lazy=True, cascade='all, delete-orphan')
    roadmaps = db.relationship('RoadmapProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    resumes = db.relationship('ResumeAnalysis', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_skills_list(self):
        if not self.technical_skills:
            return []
        return [s.strip() for s in self.technical_skills.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'education_level': self.education_level,
            'degree_specialization': self.degree_specialization,
            'current_year': self.current_year,
            'technical_skills': self.get_skills_list(),
            'technical_skills_raw': self.technical_skills or '',
            'programming_languages': self.programming_languages or '',
            'interests': self.interests or '',
            'certifications': self.certifications or '',
            'projects': self.projects or '',
            'preferred_role': self.preferred_role or '',
            'career_goals': self.career_goals or '',
            'experience_level': self.experience_level or 'Intermediate',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    readiness_score = db.Column(db.Float, default=0.0)
    match_percentage = db.Column(db.Float, default=0.0)
    matching_skills = db.Column(db.Text, default='[]')
    missing_skills = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_role': self.target_role,
            'readiness_score': round(self.readiness_score, 1),
            'match_percentage': round(self.match_percentage, 1),
            'matching_skills': json.loads(self.matching_skills) if self.matching_skills else [],
            'missing_skills': json.loads(self.missing_skills) if self.missing_skills else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RoadmapProgress(db.Model):
    __tablename__ = 'roadmap_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    duration_days = db.Column(db.Integer, default=30)
    phase_data = db.Column(db.Text, nullable=False)  # JSON representation of phases & tasks
    completed_tasks = db.Column(db.Text, default='[]')  # JSON array of completed task IDs
    progress_percentage = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        phases = json.loads(self.phase_data) if self.phase_data else []
        completed = json.loads(self.completed_tasks) if self.completed_tasks else []
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_role': self.target_role,
            'duration_days': self.duration_days,
            'phases': phases,
            'completed_tasks': completed,
            'progress_percentage': round(self.progress_percentage, 1),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    ats_score = db.Column(db.Float, default=0.0)
    extracted_skills = db.Column(db.Text, default='[]')
    matching_skills = db.Column(db.Text, default='[]')
    missing_skills = db.Column(db.Text, default='[]')
    suggestions = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'target_role': self.target_role,
            'ats_score': round(self.ats_score, 1),
            'extracted_skills': json.loads(self.extracted_skills) if self.extracted_skills else [],
            'matching_skills': json.loads(self.matching_skills) if self.matching_skills else [],
            'missing_skills': json.loads(self.missing_skills) if self.missing_skills else [],
            'suggestions': json.loads(self.suggestions) if self.suggestions else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
