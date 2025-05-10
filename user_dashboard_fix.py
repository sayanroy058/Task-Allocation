from datetime import datetime, timedelta, time
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import app, db
from models import Task, User


@app.route('/user/dashboard', endpoint='user_dashboard_fixed')
@login_required
def user_dashboard_fixed():
    """User dashboard with statistics"""
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard_fixed'))
    
    # Get current date
    today = datetime.now()
    
    # Always use the entire year
    start_date = datetime(today.year, 1, 1)
    end_date = datetime(today.year, 12, 31)
    time_period = 'year'
    
    # Get user tasks within date range - always apply date filters for consistency
    pending_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'pending',
        Task.created_at.between(start_date, end_date)
    ).count()
    
    completed_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at.between(start_date, end_date)
    ).count()
    
    edit_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'edit_requested',
        Task.created_at.between(start_date, end_date)
    ).count()
    
    # Total budget from completed tasks in date range
    total_budget = db.session.query(db.func.sum(Task.price)).filter(
        Task.user_id == current_user.id,
        Task.status == 'completed',
        Task.completed_at.between(start_date, end_date)
    ).scalar() or 0
    
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
    monthly_earnings = [0.0] * len(month_names)
    
    # Fill in chart data for each month
    for i, month_info in enumerate(month_data):
        month_start = month_info['start_date']
        month_end = month_info['end_date']
        
        # Get completed tasks for this month
        completed_in_month = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'completed',
            Task.completed_at.between(month_start, month_end)
        ).count()
        monthly_completed_tasks[i] = completed_in_month
        
        # Get pending tasks for this month
        pending_in_month = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'pending',
            Task.created_at.between(month_start, month_end)
        ).count()
        monthly_pending_tasks[i] = pending_in_month
        
        # Get edit_requested tasks for this month
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
    
    return render_template(
        'user/dashboard.html',
        pending_tasks_count=pending_tasks,
        edit_tasks_count=edit_tasks,
        total_completed=completed_tasks,
        total_budget=total_budget,
        months=month_names,
        monthly_completed_tasks=monthly_completed_tasks,
        monthly_pending_tasks=monthly_pending_tasks,
        monthly_edit_tasks=monthly_edit_tasks,
        monthly_earnings=monthly_earnings,
        current_time_period=time_period,
        start_date=start_date.strftime('%Y-%m-%d') if start_date else None,
        end_date=end_date.strftime('%Y-%m-%d') if end_date else None
    )