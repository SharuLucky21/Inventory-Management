# helpers.py
from functools import wraps
from flask import session, redirect, url_for, flash, request
from models import User, Role

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('user'):
            flash("Please login first", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash("Please login first", "warning")
                return redirect(url_for('login'))
            if user['role'] not in roles:
                flash("You don't have permission to access that page", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator
