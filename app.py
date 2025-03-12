import os
import json
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, flash, session
from openai import OpenAI
from functools import wraps
from auth import SupabaseAuth
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required")

try:
    # Initialize authentication
    auth = SupabaseAuth()
    # Initialize OpenAI client
    openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html')

        try:
            result = auth.sign_in(email, password)
            if result['success']:
                session['user'] = {
                    'id': result['user'].id,
                    'email': result['user'].email
                }
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash(result.get('error', 'Invalid email or password.'), 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('signup.html')

        try:
            result = auth.sign_up(email, password)
            if result['success']:
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash(result.get('error', 'Error creating account.'), 'danger')
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'danger')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    try:
        auth.sign_out()
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/app')
@login_required
def index():
    return render_template('index.html', templates=LESSON_TEMPLATES)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

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