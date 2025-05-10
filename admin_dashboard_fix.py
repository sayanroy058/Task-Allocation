from datetime import datetime, timedelta, time
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import app, db
from models import Task, User


@app.route('/admin/dashboard', endpoint='admin_dashboard_fixed')
@login_required
def admin_dashboard_fixed():
    """Admin dashboard with statistics"""
    if not current_user.is_admin():
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('index'))
    
    # Get current date
    today = datetime.now()
    
    # Always use the entire year
    start_date = datetime(today.year, 1, 1)
    end_date = datetime(today.year, 12, 31)
    time_period = 'year'
    
    # Get statistics for dashboard based on filter period
    total_users = User.query.filter(User.role == 'user').count()
    
    # Always apply date filters for consistency
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
    
    # Generate month labels (always show full year)
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    
    # Generate data for all months in the year
    month_data = []
    year = start_date.year
    for month in range(1, 13):
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        month_data.append({
            'year': year,
            'month': month,
            'start_date': month_start,
            'end_date': month_end
        })
    
    # Initialize arrays for chart data
    monthly_completed_tasks = [0] * len(month_names)
    monthly_pending_tasks = [0] * len(month_names)
    monthly_edit_tasks = [0] * len(month_names)
    monthly_budget = [0.0] * len(month_names)
    
    # Fill in chart data for each month
    for i, month_info in enumerate(month_data):
        month_start = month_info['start_date']
        month_end = month_info['end_date']
        
        # Get completed tasks for this month
        completed_in_month = Task.query.filter(
            Task.status == 'completed',
            Task.completed_at.between(month_start, month_end)
        ).count()
        monthly_completed_tasks[i] = completed_in_month
        
        # Get pending tasks for this month
        pending_in_month = Task.query.filter(
            Task.status == 'pending',
            Task.created_at.between(month_start, month_end)
        ).count()
        monthly_pending_tasks[i] = pending_in_month
        
        # Get edit_requested tasks for this month
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
        months=month_names,
        monthly_completed_tasks=monthly_completed_tasks,
        monthly_pending_tasks=monthly_pending_tasks,
        monthly_edit_tasks=monthly_edit_tasks,
        monthly_budget=monthly_budget,
        tasks=recent_tasks,
        current_time_period=time_period,
        start_date=start_date.strftime('%Y-%m-%d') if start_date else None,
        end_date=end_date.strftime('%Y-%m-%d') if end_date else None
    )