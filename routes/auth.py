from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from auth import supabase
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            if response.user:
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email
                }
                flash('Successfully signed up! Please check your email for verification.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to create account. Please try again.', 'error')
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'error')
    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if response.user:
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email
                }
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    session.clear()
    return redirect(url_for('landing'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            supabase.auth.reset_password_email(email)
            flash('Password reset email sent! Please check your inbox.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    return render_template('auth/reset_password.html')