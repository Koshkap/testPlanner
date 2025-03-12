import os
import json
from flask import Flask, render_template, request, jsonify, make_response, session, flash, redirect, url_for
from openai import OpenAI
from auth import login_required
from routes.auth import auth_bp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    logger.error("SESSION_SECRET environment variable not set")
    raise ValueError("SESSION_SECRET must be set")

# Configure the SQLAlchemy part of the app
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy with app
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize OpenAI client
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Create all database tables
with app.app_context():
    import models  # Import models here to avoid circular imports
    db.create_all()

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

@app.route('/')
def landing():
    if 'user' in session:
        return redirect(url_for('index'))
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
@login_required
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
@login_required
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