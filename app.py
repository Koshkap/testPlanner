import os
import logging
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session
from openai import OpenAI
from functools import wraps
from auth import SupabaseAuth, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import stripe
import logging
import json

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
    logger.error("STRIPE_PRICE_ID environment variable is missing")
    raise ValueError("STRIPE_PRICE_ID environment variable is required")

try:
    # Verify if it's a valid price ID by making a test API call
    stripe.Price.retrieve(STRIPE_PRICE_ID)
    logger.info(f"Successfully validated Stripe Price ID: {STRIPE_PRICE_ID}")
except stripe.error.InvalidRequestError as e:
    logger.error(f"Invalid Stripe Price ID: {STRIPE_PRICE_ID}")
    raise ValueError(f"Invalid Stripe Price ID: {str(e)}")

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
    """Check if the current user has an active subscription or is admin"""
    if not current_user.is_authenticated:
        return False

    # Admin users have access to all features
    if current_user.is_admin:
        return True

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
        if current_user.is_admin:
            return f(*args, **kwargs)
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
        logger.info(f"Creating checkout session for email: {customer_email}")

        customers = stripe.Customer.list(email=customer_email, limit=1)
        if customers.data:
            customer = customers.data[0]
            logger.info(f"Found existing customer with ID: {customer.id}")
        else:
            customer = stripe.Customer.create(email=customer_email)
            logger.info(f"Created new customer with ID: {customer.id}")

        session['stripe_customer_id'] = customer.id

        # Log the price ID we're using
        logger.info(f"Using Stripe Price ID: {STRIPE_PRICE_ID}")

        # Create checkout session with subscription
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'https://{YOUR_DOMAIN}/subscription-success',
            cancel_url=f'https://{YOUR_DOMAIN}/pricing',
            allow_promotion_codes=True,
            billing_address_collection='required',
        )

        logger.info(f"Created checkout session: {checkout_session.id}")
        return redirect(checkout_session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe invalid request error: {str(e)}")
        flash('Unable to process subscription. Please try again later.', 'danger')
        return redirect(url_for('pricing'))
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        flash('An error occurred with the payment processor. Please try again later.', 'danger')
        return redirect(url_for('pricing'))
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')
        return redirect(url_for('pricing'))

@app.route('/subscription-success')
@login_required
def subscription_success():
    flash('Thank you for subscribing!', 'success')
    return redirect(url_for('app_index'))

@app.route('/pricing')
def pricing():
    is_subscribed = check_subscription() if current_user.is_authenticated else False
    return render_template('pricing.html', is_subscribed=is_subscribed)

@app.route('/')
def landing():
    if current_user.is_authenticated:
        is_subscribed = check_subscription()
        if is_subscribed:
            return redirect(url_for('app_index'))
        return render_template('landing.html', is_subscribed=is_subscribed)
    return render_template('landing.html', is_subscribed=False)

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

        try:
            # Check if using demo admin credentials
            demo_email = os.environ.get('DEMO_ADMIN_EMAIL')
            demo_password = os.environ.get('DEMO_ADMIN_PASSWORD')

            if not demo_email or not demo_password:
                logger.error("Demo admin credentials not properly configured")
                flash('Authentication system is not properly configured.', 'danger')
                return render_template('login.html')

            if email == demo_email and password == demo_password:
                logger.info(f"Admin login successful for: {email}")
                # Create admin user session
                user_data = {
                    'id': 'admin',
                    'email': email,
                    'is_admin': True
                }
                user = User(user_data)
                login_user(user)
                session['user'] = user_data
                flash('Welcome, Admin!', 'success')
                return redirect(url_for('app_index'))

            # Regular user authentication
            result = auth.sign_in(email, password)
            if result['success']:
                user = result['user']
                login_user(user)
                session['user'] = {
                    'id': user.id,
                    'email': user.email,
                    'is_admin': False
                }
                flash('Successfully logged in!', 'success')
                return redirect(url_for('landing'))
            else:
                error_msg = result.get('error', 'Invalid credentials')
                flash(error_msg, 'danger')
                logger.warning(f"Failed login attempt for user: {email}")

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')

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

if __name__ == '__main__':
    app.run(debug=True)