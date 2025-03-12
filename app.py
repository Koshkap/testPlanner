import os
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
    return render_template('landing.html')

@app.route('/app')
def index():
    return render_template('index.html', templates=LESSON_TEMPLATES)

@app.route('/generate', methods=['POST'])
def generate_lesson():
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
