import os
import uuid
from datetime import datetime, timedelta
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from flask import render_template, request, redirect, url_for, flash, abort, send_from_directory, jsonify
from flask_login import login_user, current_user, logout_user, login_required

from app import db
from models import User, Task, File, TaskEdit, EditFile
from utils import send_task_notification, send_completion_notification, send_edit_notification

# Create admin user if not exists function - exported for use in app.py
def create_admin():
    """Create admin user if not exists"""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@example.com',
            mobile='0000000000',
            expertise='Administration',
            role='admin'
        )
        admin.set_password('admin123')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created")

def allowed_file(filename):
    """Check if file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'zip', 'rar', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, task_id, file_type):
    """Save a file to the uploads directory and return a unique filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # Save file in a directory structure: uploads/task_id/file_type/
        file_dir = os.path.join('uploads', str(task_id), file_type)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        
        file_path = os.path.join(file_dir, unique_filename)
        file.save(file_path)
        return unique_filename, filename
    return None, None

def get_filtered_tasks(query, filters):
    """Apply filters to task query"""
    if filters.get('task_id'):
        query = query.filter(Task.task_id.ilike(f"%{filters['task_id']}%"))
    
    if filters.get('user_id'):
        query = query.filter(Task.user_id == filters['user_id'])
    
    if filters.get('status') and filters['status'] != 'all':
        query = query.filter(Task.status == filters['status'])
    
    if filters.get('time_period'):
        today = datetime.now().date()
        if filters['time_period'] == 'today':
            query = query.filter(db.func.date(Task.created_at) == today)
        elif filters['time_period'] == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(db.func.date(Task.created_at) >= week_ago)
        elif filters['time_period'] == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(db.func.date(Task.created_at) >= month_ago)
        elif filters['time_period'] == 'year':
            year_ago = today - timedelta(days=365)
            query = query.filter(db.func.date(Task.created_at) >= year_ago)
        elif filters['time_period'] == 'custom':
            # Handle custom date range
            start_date_str = filters.get('start_date')
            end_date_str = filters.get('end_date')
            
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    query = query.filter(db.func.date(Task.created_at) >= start_date)
                except ValueError:
                    # Invalid date format, ignore filter
                    pass
            
            if end_date_str:
                try:
                    # Add one day to end date to include the end date in results
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() + timedelta(days=1)
                    query = query.filter(db.func.date(Task.created_at) < end_date)
                except ValueError:
                    # Invalid date format, ignore filter
                    pass
    
    return query

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/')
    def index():
        """Home page - redirects to appropriate dashboard based on user role"""
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        return render_template('login.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout"""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        """Change user password"""
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('user_profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('user_profile'))
        
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('user_profile'))
    
    # Admin routes
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        """Admin dashboard with statistics"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        # Get date filter parameters
        time_period = request.args.get('time_period', 'year')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get current date and set default filter period
        today = datetime.now()
        
        # Parse custom date range if provided
        custom_range = False
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                custom_range = True
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD format.', 'warning')
                start_date = None
                end_date = None
        
        # Set date range based on time period
        if not custom_range:
            if time_period == 'month':
                start_date = today.replace(day=1)
                end_date = today
            elif time_period == 'quarter':
                current_quarter = (today.month - 1) // 3
                start_date = datetime(today.year, current_quarter * 3 + 1, 1)
                if current_quarter == 3:  # Q4
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(today.year, current_quarter * 3 + 4, 1) - timedelta(days=1)
            elif time_period == 'half-year':
                if today.month <= 6:  # H1
                    start_date = datetime(today.year, 1, 1)
                    end_date = datetime(today.year, 7, 1) - timedelta(days=1)
                else:  # H2
                    start_date = datetime(today.year, 7, 1)
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
            else:  # year (default)
                start_date = datetime(today.year, 1, 1)
                end_date = datetime(today.year, 12, 31)
        
        # Get statistics for dashboard based on filter period
        total_users = User.query.filter(User.role == 'user').count()
        
        # For tasks, apply date filter only if custom range or non-year period is selected
        if custom_range or time_period != 'year':
            total_tasks = Task.query.filter(Task.created_at.between(start_date, end_date)).count()
            pending_tasks = Task.query.filter(
                Task.status == 'pending',
                Task.created_at.between(start_date, end_date)
            ).count()
            completed_tasks = Task.query.filter(
                Task.status == 'completed',
                Task.completed_at.between(start_date, end_date)
            ).count()
            editing_tasks = Task.query.filter(
                Task.status == 'edit_requested',
                Task.created_at.between(start_date, end_date)
            ).count()
        else:
            total_tasks = Task.query.count()
            pending_tasks = Task.query.filter_by(status='pending').count()
            completed_tasks = Task.query.filter_by(status='completed').count()
            editing_tasks = Task.query.filter_by(status='edit_requested').count()
        
        # Get monthly data for charts based on the selected time period
        months = []
        
        # For month view, only show the current month
        if time_period == 'month' and not custom_range:
            months = [start_date.strftime('%B')]  # Just the current month
        # For year view, show all 12 months
        elif time_period == 'year' and not custom_range:
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
        # For quarter, half-year, and custom date range
        else:
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                months.append(current_date.strftime('%B'))
                # Move to next month
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Initialize arrays for chart data
        monthly_completed_tasks = [0] * len(months)
        monthly_pending_tasks = [0] * len(months)
        monthly_edit_tasks = [0] * len(months)
        monthly_budget = [0] * len(months)
        
        # Fill in chart data for each month
        for i, month_name in enumerate(months):
            # Convert month name to month number (1-12)
            month_num = datetime.strptime(month_name, '%B').month
            
            # Get year for this month (may span years)
            year = today.year
            if month_num > today.month and custom_range and start_date.year < today.year:
                year = start_date.year
            elif month_num < today.month and custom_range and end_date.year > today.year:
                year = end_date.year
            
            # Set date range for this month
            month_start = datetime(year, month_num, 1)
            if month_num == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month_num + 1, 1) - timedelta(days=1)
            
            # Get tasks for this month by status
            completed_in_month = Task.query.filter(
                Task.status == 'completed',
                Task.completed_at.between(month_start, month_end)
            ).count()
            monthly_completed_tasks[i] = completed_in_month
            
            pending_in_month = Task.query.filter(
                Task.status == 'pending',
                Task.created_at.between(month_start, month_end)
            ).count()
            monthly_pending_tasks[i] = pending_in_month
            
            edit_in_month = Task.query.filter(
                Task.status == 'edit_requested',
                Task.created_at.between(month_start, month_end)
            ).count()
            monthly_edit_tasks[i] = edit_in_month
            
            # Get budget for this month
            month_budget = db.session.query(db.func.sum(Task.price)).filter(
                Task.created_at.between(month_start, month_end)
            ).scalar() or 0
            monthly_budget[i] = float(month_budget)
        
        # Get recent tasks for the dashboard
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        
        return render_template(
            'admin/dashboard.html',
            total_users=total_users,
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            completed_tasks=completed_tasks,
            editing_tasks=editing_tasks,
            months=months,
            monthly_completed_tasks=monthly_completed_tasks,
            monthly_pending_tasks=monthly_pending_tasks,
            monthly_edit_tasks=monthly_edit_tasks,
            monthly_budget=monthly_budget,
            tasks=recent_tasks,
            current_time_period=time_period,
            start_date=start_date.strftime('%Y-%m-%d') if start_date else None,
            end_date=end_date.strftime('%Y-%m-%d') if end_date else None
        )
    
    @app.route('/admin/users')
    @login_required
    def admin_users():
        """User management page"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        users = User.query.filter(User.role == 'user').order_by(User.name).all()
        return render_template('admin/users.html', users=users)
        
    @app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
    @login_required
    def reset_user_password(user_id):
        """Reset a user's password (admin only)"""
        if not current_user.is_admin():
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('index'))
            
        user = User.query.get_or_404(user_id)
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Both password fields are required.', 'danger')
            return redirect(url_for('admin_users'))
            
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('admin_users'))
            
        user.set_password(new_password)
        db.session.commit()
        
        flash(f'Password for {user.name} has been reset successfully.', 'success')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    def delete_user(user_id):
        """Delete a user and all their associated tasks (admin only)"""
        if not current_user.is_admin():
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('index'))
            
        user = User.query.get_or_404(user_id)
        
        # Delete all tasks associated with the user
        tasks = Task.query.filter_by(user_id=user_id).all()
        for task in tasks:
            # Delete all files associated with the task
            files = File.query.filter_by(task_id=task.id).all()
            for file in files:
                db.session.delete(file)
            
            # Delete all edits associated with the task
            edits = TaskEdit.query.filter_by(task_id=task.id).all()
            for edit in edits:
                # Delete all edit files
                edit_files = EditFile.query.filter_by(edit_id=edit.id).all()
                for edit_file in edit_files:
                    db.session.delete(edit_file)
                db.session.delete(edit)
            
            db.session.delete(task)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user.name} and all associated tasks have been deleted.', 'success')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/add', methods=['GET', 'POST'])
    @login_required
    def add_user():
        """Add new user page"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            expertise = request.form.get('expertise')
            password = request.form.get('password')
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists in the system.', 'danger')
                return redirect(url_for('add_user'))
            
            # Create new user
            user = User(
                name=name,
                email=email,
                mobile=mobile,
                expertise=expertise,
                role='user'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {name} created successfully!', 'success')
            return redirect(url_for('admin_users'))
        
        return render_template('admin/add_user.html')
    
    @app.route('/admin/tasks')
    @login_required
    def admin_tasks():
        """Task management page with filters"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        # Get filter parameters
        filters = {
            'task_id': request.args.get('task_id'),
            'user_id': request.args.get('user_id', type=int),
            'status': request.args.get('status'),
            'time_period': request.args.get('time_period'),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date')
        }
        
        # Query tasks with filters
        tasks_query = Task.query
        tasks_query = get_filtered_tasks(tasks_query, filters)
        
        # Order by created_at (newest first)
        tasks = tasks_query.order_by(Task.created_at.desc()).all()
        
        # Get all users for the user filter dropdown
        users = User.query.filter(User.role == 'user').order_by(User.name).all()
        
        return render_template(
            'admin/all_tasks.html', 
            tasks=tasks, 
            users=users,
            request=request
        )
    
    @app.route('/admin/tasks/add', methods=['GET', 'POST'])
    @login_required
    def add_task():
        """Add new task page"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            user_id = request.form.get('user_id', type=int)
            description = request.form.get('description')
            deadline_str = request.form.get('deadline')
            price = request.form.get('price', type=float)
            
            # Validate inputs
            if not user_id or not description or not deadline_str or not price:
                flash('All fields are required.', 'danger')
                return redirect(url_for('add_task'))
            
            # Parse deadline
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid deadline format.', 'danger')
                return redirect(url_for('add_task'))
            
            # Create new task
            task = Task(
                user_id=user_id,
                description=description,
                deadline=deadline,
                price=price,
                status='pending'
            )
            
            db.session.add(task)
            db.session.commit()
            
            # Save files if provided
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    filename, original_filename = save_file(file, task.id, 'task')
                    if filename:
                        file_record = File(
                            filename=filename,
                            original_filename=original_filename,
                            file_type='task',
                            task_id=task.id
                        )
                        db.session.add(file_record)
            
            db.session.commit()
            
            # Send notification email
            user = User.query.get(user_id)
            try:
                send_task_notification(user.email, task.task_id, description, deadline)
            except Exception as e:
                logging.error(f"Failed to send task notification: {e}")
            
            flash(f'Task {task.task_id} assigned to {user.name} successfully!', 'success')
            return redirect(url_for('admin_tasks'))
        
        # Get all users for the dropdown
        users = User.query.filter(User.role == 'user').order_by(User.name).all()
        return render_template('admin/add_task.html', users=users)
    
    @app.route('/admin/tasks/<task_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_edit_task(task_id):
        """Request edits for a completed task"""
        if not current_user.is_admin():
            flash('You do not have permission to access the admin area.', 'danger')
            return redirect(url_for('index'))
        
        task = Task.query.filter_by(task_id=task_id).first_or_404()
        
        # Check if task is completed
        if task.status != 'completed':
            flash('Only completed tasks can be edited.', 'warning')
            return redirect(url_for('admin_tasks'))
        
        if request.method == 'POST':
            instructions = request.form.get('instructions')
            
            if not instructions:
                flash('Instructions are required.', 'danger')
                return redirect(url_for('admin_edit_task', task_id=task_id))
            
            # Create edit request
            edit_request = TaskEdit(
                instructions=instructions,
                task_id=task.id,
                status='pending'
            )
            
            db.session.add(edit_request)
            db.session.commit()
            
            # Save instruction files if provided
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    filename, original_filename = save_file(file, edit_request.id, 'instruction')
                    if filename:
                        file_record = EditFile(
                            filename=filename,
                            original_filename=original_filename,
                            file_type='instruction',
                            edit_id=edit_request.id
                        )
                        db.session.add(file_record)
            
            # Update task status
            task.status = 'edit_requested'
            db.session.commit()
            
            # Send notification email
            try:
                send_edit_notification(task.assigned_user.email, task.task_id, instructions)
            except Exception as e:
                logging.error(f"Failed to send edit notification: {e}")
            
            flash(f'Edit request sent for task {task.task_id} successfully!', 'success')
            return redirect(url_for('admin_tasks'))
        
        return render_template('admin/edit_task.html', task=task)
    
    @app.route('/api/tasks/<int:task_id>')
    @login_required
    def get_task_details(task_id):
        """API endpoint to get task details for the modal"""
        if not current_user.is_admin() and not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        task = Task.query.get_or_404(task_id)
        
        # For regular users, only allow access to their own tasks
        if not current_user.is_admin() and task.user_id != current_user.id:
            return jsonify({'error': 'You do not have permission to view this task'}), 403
        
        # Format the task data as JSON
        task_data = {
            'id': task.id,
            'task_id': task.task_id,
            'description': task.description,
            'deadline': task.deadline.isoformat(),
            'price': task.price,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'user_id': task.user_id,
            'user_name': task.assigned_user.name,
            'files': {
                'task': [{'filename': f.filename, 'original_filename': f.original_filename} 
                        for f in task.files if f.file_type == 'task'],
                'submission': [{'filename': f.filename, 'original_filename': f.original_filename} 
                               for f in task.files if f.file_type == 'submission']
            },
            'edits': [{
                'id': edit.id,
                'instructions': edit.instructions,
                'status': edit.status,
                'created_at': edit.created_at.isoformat(),
                'completed_at': edit.completed_at.isoformat() if edit.completed_at else None,
                'files': {
                    'instruction': [{'filename': f.filename, 'original_filename': f.original_filename} 
                                   for f in edit.files if f.file_type == 'instruction'],
                    'submission': [{'filename': f.filename, 'original_filename': f.original_filename} 
                                  for f in edit.files if f.file_type == 'submission']
                }
            } for edit in task.edits]
        }
        
        return jsonify(task_data)
    
    @app.route('/download/<file_type>/<filename>')
    @login_required
    def download_file(file_type, filename):
        """Download a file"""
        if file_type == 'task':
            # Find the task file
            file_record = File.query.filter_by(filename=filename, file_type='task').first_or_404()
            task = Task.query.get(file_record.task_id)
            
            # Check permissions
            if not current_user.is_admin() and current_user.id != task.user_id:
                abort(403)
            
            file_path = os.path.join('uploads', str(task.id), 'task')
        
        elif file_type == 'submission':
            # Find the submission file
            file_record = File.query.filter_by(filename=filename, file_type='submission').first_or_404()
            task = Task.query.get(file_record.task_id)
            
            # Check permissions
            if not current_user.is_admin() and current_user.id != task.user_id:
                abort(403)
            
            file_path = os.path.join('uploads', str(task.id), 'submission')
        
        elif file_type == 'edit':
            # Find the edit file
            file_record = EditFile.query.filter_by(filename=filename).first_or_404()
            edit = TaskEdit.query.get(file_record.edit_id)
            task = Task.query.get(edit.task_id)
            
            # Check permissions
            if not current_user.is_admin() and current_user.id != task.user_id:
                abort(403)
            
            file_path = os.path.join('uploads', str(edit.id), 'instruction')
        
        else:
            abort(404)
        
        return send_from_directory(file_path, filename, as_attachment=True)
    
    # User routes
    @app.route('/dashboard')
    @login_required
    def user_dashboard():
        """User dashboard with statistics"""
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        
        # Get date filter parameters
        time_period = request.args.get('time_period', 'year')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get current date and set default filter period
        today = datetime.now()
        
        # Parse custom date range if provided
        custom_range = False
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                custom_range = True
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD format.', 'warning')
                start_date = None
                end_date = None
        
        # Set date range based on time period
        if not custom_range:
            if time_period == 'month':
                start_date = today.replace(day=1)
                end_date = today
            elif time_period == 'quarter':
                current_quarter = (today.month - 1) // 3
                start_date = datetime(today.year, current_quarter * 3 + 1, 1)
                if current_quarter == 3:  # Q4
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(today.year, current_quarter * 3 + 4, 1) - timedelta(days=1)
            elif time_period == 'half-year':
                if today.month <= 6:  # H1
                    start_date = datetime(today.year, 1, 1)
                    end_date = datetime(today.year, 7, 1) - timedelta(days=1)
                else:  # H2
                    start_date = datetime(today.year, 7, 1)
                    end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
            else:  # year (default)
                start_date = datetime(today.year, 1, 1)
                end_date = datetime(today.year, 12, 31)
        
        # Get user's tasks by status for the stats section
        # For tasks, apply date filter only if custom range or non-year period is selected
        if custom_range or time_period != 'year':
            pending_tasks_count = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'pending',
                Task.created_at.between(start_date, end_date)
            ).count()
            
            edit_tasks_count = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'edit_requested',
                Task.created_at.between(start_date, end_date)
            ).count()
            
            total_completed = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'completed',
                Task.completed_at.between(start_date, end_date)
            ).count()
            
            total_budget = db.session.query(db.func.sum(Task.price)).filter(
                Task.user_id == current_user.id,
                Task.status == 'completed',
                Task.completed_at.between(start_date, end_date)
            ).scalar() or 0
        else:
            pending_tasks_count = Task.query.filter_by(
                user_id=current_user.id, 
                status='pending'
            ).count()
            
            edit_tasks_count = Task.query.filter_by(
                user_id=current_user.id, 
                status='edit_requested'
            ).count()
            
            total_completed = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'completed'
            ).count()
            
            total_budget = db.session.query(db.func.sum(Task.price)).filter(
                Task.user_id == current_user.id,
                Task.status == 'completed'
            ).scalar() or 0
        
        # Get monthly data for charts based on the selected time period
        months = []
        
        # For month view, only show the current month
        if time_period == 'month' and not custom_range:
            months = [start_date.strftime('%B')]  # Just the current month
        # For year view, show all 12 months
        elif time_period == 'year' and not custom_range:
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        # For quarter, half-year, and custom date range
        else:
            # Get months in the date range
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                months.append(current_date.strftime('%B'))
                # Move to next month
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Initialize arrays for chart data
        monthly_completed_tasks = [0] * len(months)
        monthly_pending_tasks = [0] * len(months)
        monthly_edit_tasks = [0] * len(months)
        monthly_earnings = [0] * len(months)
        
        # Fill in chart data for each month
        for i, month_name in enumerate(months):
            # Convert month name to month number (1-12)
            month_num = datetime.strptime(month_name, '%B').month
            
            # Get year for this month (may span years)
            year = today.year
            if month_num > today.month and custom_range and start_date.year < today.year:
                year = start_date.year
            elif month_num < today.month and custom_range and end_date.year > today.year:
                year = end_date.year
            
            # Set date range for this month
            month_start = datetime(year, month_num, 1)
            if month_num == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month_num + 1, 1) - timedelta(days=1)
            
            # Get tasks for this month by status
            completed_in_month = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'completed',
                Task.completed_at.between(month_start, month_end)
            ).count()
            monthly_completed_tasks[i] = completed_in_month
            
            pending_in_month = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'pending',
                Task.created_at.between(month_start, month_end)
            ).count()
            monthly_pending_tasks[i] = pending_in_month
            
            edit_in_month = Task.query.filter(
                Task.user_id == current_user.id,
                Task.status == 'edit_requested',
                Task.created_at.between(month_start, month_end)
            ).count()
            monthly_edit_tasks[i] = edit_in_month
            
            # Get earnings for this month
            month_earnings = db.session.query(db.func.sum(Task.price)).filter(
                Task.user_id == current_user.id,
                Task.status == 'completed',
                Task.completed_at.between(month_start, month_end)
            ).scalar() or 0
            monthly_earnings[i] = float(month_earnings)
        
        # Get recent tasks for the dashboard
        recent_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()
        
        return render_template(
            'user/dashboard.html',
            pending_tasks_count=pending_tasks_count,
            edit_tasks_count=edit_tasks_count,
            total_completed=total_completed,
            total_budget=total_budget,
            months=months,
            monthly_completed_tasks=monthly_completed_tasks,
            monthly_pending_tasks=monthly_pending_tasks,
            monthly_edit_tasks=monthly_edit_tasks,
            monthly_earnings=monthly_earnings,
            tasks=recent_tasks,
            current_time_period=time_period,
            start_date=start_date.strftime('%Y-%m-%d') if start_date else None,
            end_date=end_date.strftime('%Y-%m-%d') if end_date else None
        )
    
    @app.route('/tasks')
    @login_required
    def user_tasks():
        """User's tasks with filters"""
        if current_user.is_admin():
            return redirect(url_for('admin_tasks'))
        
        # Get filter parameters
        status = request.args.get('status', 'all')
        time_period = request.args.get('time_period')
        
        # Query user's tasks
        tasks_query = Task.query.filter_by(user_id=current_user.id)
        
        # Apply status filter
        if status != 'all':
            tasks_query = tasks_query.filter_by(status=status)
        
        # Apply time period filter
        if time_period:
            today = datetime.now().date()
            if time_period == 'today':
                tasks_query = tasks_query.filter(db.func.date(Task.created_at) == today)
            elif time_period == 'week':
                week_ago = today - timedelta(days=7)
                tasks_query = tasks_query.filter(db.func.date(Task.created_at) >= week_ago)
            elif time_period == 'month':
                month_ago = today - timedelta(days=30)
                tasks_query = tasks_query.filter(db.func.date(Task.created_at) >= month_ago)
            elif time_period == 'year':
                year_ago = today - timedelta(days=365)
                tasks_query = tasks_query.filter(db.func.date(Task.created_at) >= year_ago)
        
        # Order by created_at (newest first)
        tasks = tasks_query.order_by(Task.created_at.desc()).all()
        
        return render_template(
            'user/tasks.html', 
            tasks=tasks, 
            status=status
        )
    
    @app.route('/edits')
    @login_required
    def user_edits():
        """User's tasks that need edits"""
        if current_user.is_admin():
            return redirect(url_for('admin_tasks'))
        
        tasks = Task.query.filter_by(
            user_id=current_user.id, 
            status='edit_requested'
        ).order_by(Task.created_at.desc()).all()
        
        return render_template('user/edit_tasks.html', tasks=tasks)
    
    @app.route('/profile')
    @login_required
    def user_profile():
        """User profile page"""
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        
        # Get task counts
        pending_tasks_count = Task.query.filter_by(
            user_id=current_user.id, 
            status='pending'
        ).count()
        
        completed_tasks_count = Task.query.filter_by(
            user_id=current_user.id, 
            status='completed'
        ).count()
        
        edit_tasks_count = Task.query.filter_by(
            user_id=current_user.id, 
            status='edit_requested'
        ).count()
        
        # Calculate total earnings from completed tasks
        completed_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status.in_(['completed', 'edit_requested'])
        ).all()
        
        total_earnings = sum(task.price for task in completed_tasks)
        
        return render_template(
            'user/profile.html',
            pending_tasks_count=pending_tasks_count,
            completed_tasks_count=completed_tasks_count,
            edit_tasks_count=edit_tasks_count,
            total_earnings=total_earnings
        )
    
    @app.route('/tasks/<task_id>/submit', methods=['POST'])
    @login_required
    def submit_task(task_id):
        """Submit a completed task"""
        if current_user.is_admin():
            flash('Admins cannot submit tasks.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        task = Task.query.filter_by(task_id=task_id).first_or_404()
        
        # Check if task belongs to user
        if task.user_id != current_user.id:
            abort(403)
        
        # Check if task is in pending status
        if task.status != 'pending':
            flash('Only pending tasks can be submitted.', 'warning')
            return redirect(url_for('user_tasks'))
        
        # Check if files are provided
        if 'files' not in request.files:
            flash('No files uploaded.', 'danger')
            return redirect(url_for('user_tasks'))
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('No files selected.', 'danger')
            return redirect(url_for('user_tasks'))
        
        # Save submission files
        for file in files:
            if file and file.filename:
                filename, original_filename = save_file(file, task.id, 'submission')
                if filename:
                    file_record = File(
                        filename=filename,
                        original_filename=original_filename,
                        file_type='submission',
                        task_id=task.id
                    )
                    db.session.add(file_record)
        
        # Update task status
        task.status = 'completed'
        task.completed_at = datetime.now()
        db.session.commit()
        
        # Send notification email
        try:
            send_completion_notification(task.task_id, current_user.name)
        except Exception as e:
            logging.error(f"Failed to send completion notification: {e}")
        
        flash(f'Task {task.task_id} submitted successfully!', 'success')
        return redirect(url_for('user_tasks'))
    
    @app.route('/edits/<task_id>/submit', methods=['POST'])
    @login_required
    def submit_edit(task_id):
        """Submit a completed edit"""
        if current_user.is_admin():
            flash('Admins cannot submit edits.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        task = Task.query.filter_by(task_id=task_id).first_or_404()
        
        # Check if task belongs to user
        if task.user_id != current_user.id:
            abort(403)
        
        # Check if task is in edit_requested status
        if task.status != 'edit_requested':
            flash('Only tasks with requested edits can be updated.', 'warning')
            return redirect(url_for('user_edits'))
        
        # Check if files are provided
        if 'files' not in request.files:
            flash('No files uploaded.', 'danger')
            return redirect(url_for('user_edits'))
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('No files selected.', 'danger')
            return redirect(url_for('user_edits'))
        
        # Get latest edit request
        edit_request = TaskEdit.query.filter_by(
            task_id=task.id
        ).order_by(TaskEdit.created_at.desc()).first()
        
        if not edit_request:
            flash('No edit request found for this task.', 'danger')
            return redirect(url_for('user_edits'))
        
        # Save submission files
        for file in files:
            if file and file.filename:
                filename, original_filename = save_file(file, edit_request.id, 'submission')
                if filename:
                    file_record = EditFile(
                        filename=filename,
                        original_filename=original_filename,
                        file_type='submission',
                        edit_id=edit_request.id
                    )
                    db.session.add(file_record)
        
        # Update edit request status
        edit_request.status = 'completed'
        edit_request.completed_at = datetime.now()
        
        # Update task status
        task.status = 'completed'
        task.completed_at = datetime.now()
        db.session.commit()
        
        # Send notification email
        try:
            send_completion_notification(task.task_id, current_user.name, is_edit=True)
        except Exception as e:
            logging.error(f"Failed to send edit completion notification: {e}")
        
        flash(f'Edit for task {task.task_id} submitted successfully!', 'success')
        return redirect(url_for('user_edits'))
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500