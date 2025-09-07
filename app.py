import os
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
    """
    A simple health check endpoint to verify that the server is running.
    """
    response_data = {
        "status": "OK",
        "message": "LMS backend is healthy and running."
    }
    return jsonify(response_data)

@app.route('/api/courses/generate', methods=['POST'])
def generate_course_plan():
    """
    Generates a personalized course plan by invoking the CourseCreatorAgent.
    Expects a JSON body with user's professional profile.
    """
    profile_data = request.get_json()
    if not profile_data:
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    experience = profile_data.get('experience')
    tech_stack = profile_data.get('techStack')
    expected_role = profile_data.get('expectedRole')

    if not all([experience, tech_stack, expected_role]):
        return jsonify({"error": "Missing required fields: experience, techStack, expectedRole"}), 400

    prompt = (
        f"Create a personalized learning plan for a user with the following profile: "
        f"Years of Experience: {experience}. "
        f"Current Tech Stack: {tech_stack}. "
        f"Aspiring to be a: {expected_role}. "
        "The plan should be structured into weekly modules, with specific, actionable tasks for each week. "
        "Return the output as a clean JSON object without any surrounding text or markdown formatting."
    )

    try:
        print(f"Invoking real CourseCreatorAgent with prompt: {prompt}")
        course_plan = invoke_course_creator_agent(prompt)
        return jsonify(course_plan)
    except Exception as e:
        print(f"Error invoking CourseCreatorAgent: {e}")
        return jsonify({"error": "Failed to generate course plan from agent.", "details": str(e)}), 500


@app.route('/api/course/content', methods=['POST'])
def get_topic_content():
    """
    Fetches the learning content for a specific topic using the TrainerAgent.
    Expects a JSON body with the course and topic titles.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    course_title = data.get('courseTitle')
    topic_title = data.get('topicTitle')

    if not all([course_title, topic_title]):
        return jsonify({"error": "Missing required fields: courseTitle, topicTitle"}), 400

    prompt = (
        f"Generate detailed learning content for the topic '{topic_title}' "
        f"which is part of the course '{course_title}'. The content should include "
        f"a detailed explanation, hyperlinks to relevant external resources, "
        f"and indicate if a quiz should follow the content. Return the output as a clean JSON object "
        f"without any surrounding text or markdown formatting."
    )

    try:
        print(f"Invoking real TrainerAgent with prompt: {prompt}")
        content_details = invoke_trainer_agent(prompt)
        return jsonify(content_details)
    except Exception as e:
        print(f"Error invoking TrainerAgent: {e}")
        return jsonify({"error": "Failed to fetch topic content from agent.", "details": str(e)}), 500

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    """
    Generates a 3-question quiz for a specific topic using the TrainerAgent.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    course_title = data.get('courseTitle')
    topic_title = data.get('topicTitle')

    if not all([course_title, topic_title]):
        return jsonify({"error": "Missing required fields: courseTitle, topicTitle"}), 400

    prompt = (
        f"Act as a senior software engineering instructor. Create a 3-question multiple-choice quiz "
        f"about the React topic '{topic_title}' from the course '{course_title}'. "
        f"Use your internal knowledge to generate the questions and answers. "
        "The response must be a clean JSON object with a single key 'questions'. "
        "The value of 'questions' should be an array of objects. Each object should have: "
        "1. A 'question' key with the question text (string). "
        "2. An 'options' key with an array of 4 string options. "
        "3. An 'answer' key with the string of the correct option. "
        "Do not include any other text or markdown formatting in the response."
    )

    try:
        print(f"Invoking TrainerAgent for quiz generation with prompt: {prompt}")
        quiz_data = invoke_trainer_agent(prompt)
        return jsonify(quiz_data)
    except Exception as e:
        print(f"Error invoking TrainerAgent for quiz: {e}")
        return jsonify({"error": "Failed to generate quiz from agent.", "details": str(e)}), 500

@app.route('/api/chatbot/query', methods=['POST'])
def chatbot_query():
    """
    Handles a user's query for the AI chatbot using the TrainerAgent.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be a valid JSON"}), 400

    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "Missing required field: query"}), 400

    # This prompt instructs the agent on its persona and the desired output format.
    prompt = (
        f"You are an expert AI learning assistant for software developers. A student has asked the "
        f"following question: '{user_query}'. Provide a clear, helpful, and concise answer. "
        f"Return the response as a clean JSON object with a single key 'answer' which contains your text response. "
        f"Do not include any other text or markdown formatting."
    )

    try:
        print(f"Invoking TrainerAgent for chatbot with prompt: {prompt}")
        agent_response = invoke_trainer_agent(prompt)
        return jsonify(agent_response)
    except Exception as e:
        print(f"Error invoking TrainerAgent for chatbot: {e}")
        return jsonify({"error": "Failed to get answer from agent.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

