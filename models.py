import secrets
import string
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

def generate_task_id(length=8):
    """Generate a unique alphanumeric task ID"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    expertise = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='assigned_user', lazy=True)
    
    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.name} ({self.email})>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(10), unique=True, nullable=False, default=generate_task_id)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)  # In INR
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'edit_requested'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    files = db.relationship('File', backref='task', lazy=True)
    edits = db.relationship('TaskEdit', backref='task', lazy=True)
    
    def __repr__(self):
        return f'<Task {self.task_id} ({self.status})>'

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'task' or 'submission'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    def __repr__(self):
        return f'<File {self.original_filename} ({self.file_type})>'

class TaskEdit(db.Model):
    __tablename__ = 'task_edits'
    
    id = db.Column(db.Integer, primary_key=True)
    instructions = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # Relationships
    files = db.relationship('EditFile', backref='edit', lazy=True)
    
    def __repr__(self):
        return f'<TaskEdit for Task {self.task_id} ({self.status})>'

class EditFile(db.Model):
    __tablename__ = 'edit_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'instruction' or 'submission'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    edit_id = db.Column(db.Integer, db.ForeignKey('task_edits.id'), nullable=False)
    
    def __repr__(self):
        return f'<EditFile {self.original_filename} ({self.file_type})>'