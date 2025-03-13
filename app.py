import os
import json
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session
from openai import OpenAI
from functools import wraps
from auth import SupabaseAuth, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import stripe
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required")

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID")  # Updated to use environment variable
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

if not STRIPE_PRICE_ID:
    raise ValueError("STRIPE_PRICE_ID environment variable is required")

try:
    # Initialize authentication
    auth = SupabaseAuth()
    # Initialize OpenAI client
    openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

def check_subscription():
    """Check if the current user has an active subscription"""
    if not current_user.is_authenticated:
        return False

    try:
        # Get customer ID from session or query Stripe
        customer_id = session.get('stripe_customer_id')
        if not customer_id:
            # Search for customer by email
            customers = stripe.Customer.list(email=current_user.email, limit=1)
            if customers.data:
                customer_id = customers.data[0].id
                session['stripe_customer_id'] = customer_id
            else:
                return False

        # Check for active subscription
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            limit=1
        )
        return len(subscriptions.data) > 0
    except Exception as e:
        logger.error(f"Error checking subscription: {str(e)}")
        return False

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_subscription():
            flash('Please subscribe to access this feature.', 'warning')
            return redirect(url_for('pricing'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    if not session.get('user'):
        return None
    return User(session['user'])

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        # Get or create customer
        customer_email = current_user.email
        customers = stripe.Customer.list(email=customer_email, limit=1)

        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(email=customer_email)

        session['stripe_customer_id'] = customer.id

        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'https://{YOUR_DOMAIN}/subscription-success',
            cancel_url=f'https://{YOUR_DOMAIN}/pricing',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        flash('An error occurred while processing your request.', 'danger')
        return redirect(url_for('pricing'))

@app.route('/subscription-success')
@login_required
def subscription_success():
    flash('Thank you for subscribing!', 'success')
    return redirect(url_for('app_index'))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', is_subscribed=check_subscription() if current_user.is_authenticated else False)

@app.route('/')
def landing():
    if current_user.is_authenticated and check_subscription():
        return redirect(url_for('app_index'))
    return render_template('landing.html')

@app.route('/app')
@login_required
@subscription_required
def app_index():
    return render_template('index.html', templates=LESSON_TEMPLATES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html')

        # Hard-coded authentication for testing
        # This will allow any login to succeed for testing purposes
        session['user'] = {
            'id': '123',
            'email': email
        }
        user = User(session['user'])
        login_user(user)
        return redirect(url_for('landing'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('signup.html')

        # Validate password strength
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html')

        try:
            result = auth.sign_up(email, password)
            if result['success']:
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                error_msg = result.get('error', 'Error creating account.')
                logger.warning(f"Signup failed: {error_msg}")

                # Provide more user-friendly error messages
                if 'rate_limit' in error_msg.lower():
                    flash('Too many signup attempts. Please try again later.', 'danger')
                elif 'already' in error_msg.lower() and 'exists' in error_msg.lower():
                    flash('An account with this email already exists. Please log in instead.', 'danger')
                else:
                    flash(error_msg, 'danger')
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'danger')

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    try:
        auth.sign_out()
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate_lesson():
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())
    try:
        data = request.json
        template_type = data.get('template')
        subject = data.get('subject')
        grade = data.get('grade', '')
        duration = data.get('duration', '')
        objectives = data.get('objectives', '')
        subtemplate = data.get('subtemplate', '')

        prompt = f"""
        Create a detailed educational plan using the following parameters:
        Template Type: {LESSON_TEMPLATES[template_type]['description']}
        {"Subtemplate: " + subtemplate if subtemplate else ""}
        Subject: {subject}
        {"Grade Level: " + grade if grade else ""}
        {"Duration: " + duration if duration else ""}
        {"Objectives: " + objectives if objectives else ""}

        Please provide the plan in JSON format with the following structure:
        {{
            "title": "Title",
            "overview": "Brief overview",
            "overview_summary": ["Summary sentence 1", "Summary sentence 2"],
            "objectives": ["objective1", "objective2"],
            "objectives_summary": ["Summary sentence 1", "Summary sentence 2"],
            "materials": ["material1", "material2"],
            "materials_summary": ["Summary sentence 1", "Summary sentence 2"],
            "procedure": ["step1", "step2"],
            "procedure_summary": ["Summary sentence 1", "Summary sentence 2"],
            "assessment": "Assessment details",
            "assessment_summary": ["Summary sentence 1", "Summary sentence 2"],
            "extensions": ["extension1", "extension2"],
            "extensions_summary": ["Summary sentence 1", "Summary sentence 2"]
        }}
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return jsonify(json.loads(response.choices[0].message.content))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_resources', methods=['POST'])
def generate_resources():
    try:
        data = request.json
        prompt = data.get('prompt', '')

        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[{
                "role": "user",
                "content": f"{prompt}\nRespond in JSON format with two arrays: 'videos' and 'worksheets'"
            }],
            response_format={"type": "json_object"}
        )

        resources = json.loads(response.choices[0].message.content)
        return jsonify(resources)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

LESSON_TEMPLATES = {
    "lesson": {
        "description": "Create comprehensive lesson plans with clear objectives, activities, and methods",
        "subtemplates": {
            "Basic Frameworks": [
                "5 E's Lesson Plan",
                "Lesson Seed", 
                "Horizontal Lesson Planner",
                "SPARK Lesson"
            ],
            "Learning Approaches": [
                "Student-Centered Approach",
                "Project Based Learning",
                "Team Based Activity", 
                "Universal Design for Learning"
            ],
            "Content Organization": [
                "Unit Plan",
                "Book Summary",
                "Vocabulary List",
                "Notes Outline"
            ],
            "Special Focus": [
                "STEM Project",
                "Technology Integration", 
                "Lab + Material List",
                "Learning Situations"
            ]
        }
    },
    "assessment": {
        "description": "Generate assessment materials, rubrics, and evaluation tools",
        "subtemplates": {
            "Question Types": [
                "Multiple Choice Questions",
                "Word Problems",
                "Fill In The Blank", 
                "True/False Questions"
            ],
            "Evaluation Tools": [
                "Analytic Rubric",
                "Holistic Rubric",
                "Assessment Outline",
                "Evidence Statements" 
            ]
        }
    },
    "feedback": {
        "description": "Design engaging activities and feedback mechanisms",
        "subtemplates": {
            "Interactive Activities": [
                "Think-Pair-Share",
                "Jigsaw Activity",
                "Round Robin",
                "4 Corners"
            ],
            "Learning Games": [
                "Bingo Style",
                "Jeopardy Style",
                "Quiz Quiz Trade",
                "Escape Room"
            ],
            "Engagement Tools": [
                "Class Poll",
                "Self-Assessment",
                "Reflective Journaling",
                "Mad Lib"
            ]
        }
    }
}