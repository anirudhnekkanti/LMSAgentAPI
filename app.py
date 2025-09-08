import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Import functions to interact with the Bedrock agents
from bedrock_agents import invoke_course_creator_agent, invoke_trainer_agent

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)


# --- API Endpoints ---

@app.route('/api/health', methods=['GET'])
def health_check():
    """A simple health check endpoint."""
    return jsonify({"status": "OK", "message": "LMS backend is healthy."})

@app.route('/api/courses/generate', methods=['POST'])
def generate_course_plan():
    """Generates a personalized course plan by invoking the CourseCreatorAgent."""
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    experience = profile_data.get('experience')
    tech_stack = profile_data.get('techStack')
    expected_role = profile_data.get('expectedRole')

    if not all([experience, tech_stack, expected_role]):
        return jsonify({"error": "Missing required fields"}), 400

    # REFINED PROMPT: This prompt is highly specific to force the agent to return the exact JSON structure the frontend needs.
    prompt = (
        f"Your single task is to generate a JSON object for a learning plan for a user with {experience} of experience as a {tech_stack} who has joined {expected_role}. "
        f"The plan must span 6 weeks.\n"
        f"The JSON object must have a root key 'content' which is an array of week objects.\n"
        f"Each week object in the array must have:\n"
        f"1. An 'id' (string, e.g., 'week1').\n"
        f"2. A 'title' (string, e.g., 'Week 1: Foundational Concepts').\n"
        f"3. A 'tasks' key, which is an array of 3 to 5 task objects.\n"
        f"Each task object must have:\n"
        f"1. An 'id' (string, e.g., 'task-1', 'task-2', and must be unique).\n"
        f"2. A 'title' (string, the name of the topic).\n"
        f"3. A 'completed' key (boolean, set to false).\n"
        f"The JSON object must also have a root key 'progress' with 'completed' (number, set to 0), 'total' (number, the total count of all tasks you generate), and 'percentage' (number, set to 0).\n"
        f"Return ONLY the raw JSON object. Do not include any other text or markdown."
    )


    try:
        print(f"Invoking CourseCreatorAgent with prompt: {prompt}")
        agent_response_json = invoke_course_creator_agent(prompt)

        # No transformation is needed; the agent's response is returned directly.
        return jsonify(agent_response_json)

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error while processing course plan: {e}")
        return jsonify({"error": "Agent returned a malformed JSON response for the course plan."}), 500
    except Exception as e:
        print(f"Error invoking CourseCreatorAgent: {e}")
        return jsonify({"error": "Failed to generate course plan from agent.", "details": str(e)}), 500


@app.route('/api/course/content', methods=['POST'])
def get_topic_content():
    """Fetches learning content for a specific topic using the TrainerAgent."""
    data = request.get_json()
    course_title = data.get('courseTitle')
    topic_title = data.get('topicTitle')

    if not all([course_title, topic_title]):
        return jsonify({"error": "Missing required fields: courseTitle, topicTitle"}), 400

    # REFINED PROMPT: This is highly specific to force the agent into returning a consistent JSON structure.
    prompt = (
        f"Act as an expert software development instructor. Your single task is to generate a JSON object containing learning content for the topic '{topic_title}', which is part of the course '{course_title}'. Use your own internal knowledge. Do not search any knowledge base.\n"
        f"The JSON response must be structured as follows:\n"
        f"1. A root object with two keys: 'content' (an object) and 'quizAvailable' (a boolean set to true).\n"
        f"2. The 'content' object must contain:\n"
        f"   a. 'title' (string): The title of the topic.\n"
        f"   b. 'description' (string): A detailed overview of the topic.\n"
        f"   c. 'sections' (an array of objects): Break down the topic into several logical sections. Each object in this array must have a 'title' (string) and 'content' (string).\n"
        f"   d. 'external_links' (an array of objects): Provide relevant external URLs. Each object must have a 'title' (string) and a 'url' (string). If no links are applicable, return an empty array [].\n"
        f"Return ONLY the raw JSON object. Do not include any other text, explanations, or markdown formatting."
    )

    try:
        print(f"Invoking TrainerAgent for topic content with prompt: {prompt}")
        content_details = invoke_trainer_agent(prompt)
        return jsonify(content_details)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error while fetching topic content: {e}")
        return jsonify({"error": "Agent returned a malformed JSON for topic content."}), 500
    except Exception as e:
        print(f"Error invoking TrainerAgent for topic content: {e}")
        return jsonify({"error": "Failed to fetch topic content from agent.", "details": str(e)}), 500


@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generates a 3-question quiz for a specific topic."""
    data = request.get_json()
    course_title = data.get('courseTitle')
    topic_title = data.get('topicTitle')

    if not all([course_title, topic_title]):
        return jsonify({"error": "Missing required fields"}), 400

    prompt = (
        f"Act as an expert instructor. Create a 3-question multiple-choice quiz "
        f"about the topic '{topic_title}'. Use your internal knowledge. "
        f"The response must be a clean JSON object with a single 'questions' key. "
        f"Each question should have 'question', 'options', and 'answer' keys."
    )
    
    try:
        quiz_data = invoke_trainer_agent(prompt)
        return jsonify(quiz_data)
    except Exception as e:
        return jsonify({"error": "Failed to generate quiz.", "details": str(e)}), 500


@app.route('/api/chatbot/query', methods=['POST'])
def chatbot_query():
    """Handles a user's query for the AI chatbot."""
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "Missing required field: query"}), 400

    prompt = (
        f"You are an AI learning assistant. A student asked: '{user_query}'. "
        f"Provide a helpful, concise answer. Return the response as a JSON object "
        f"with a single key 'answer'."
    )

    try:
        agent_response = invoke_trainer_agent(prompt)
        return jsonify(agent_response)
    except Exception as e:
        return jsonify({"error": "Failed to get answer from agent.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)