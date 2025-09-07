AI-Powered LMS Backend - Step 6: AI Chatbot Integration

This step adds the final core feature: a conversational AI chatbot. A new endpoint allows the frontend to send user questions to the TrainerAgent and receive helpful answers.
Project Structure

/
├── app.py # Main Flask application with API routes
├── bedrock_agents.py # Module for making REAL calls to AWS Bedrock agents
├── requirements.txt # Python dependencies
├── .env.example # Template for your environment variables
└── README.md # This file

⚠️ Important: Configuration is Required

This version of the code will not work without proper configuration.

    AWS Credentials:

        The most secure way to configure credentials for local development is with the AWS CLI. If you haven't already, install it and run:

        aws configure

        Enter your Access Key ID, Secret Access Key, and default region. The Python boto3 library will automatically and securely find these credentials.

    Environment Variables:

        Create a new file named .env in your project's root directory.

        Copy the content from .env.example into your new .env file.

        Fill in the placeholder values:

            AWS_REGION_NAME: The AWS region where your Bedrock agents are deployed (e.g., us-east-1).

            COURSE_CREATOR_AGENT_ID: Find this in the AWS Bedrock console on your agent's overview page.

            COURSE_CREATOR_AGENT_ALIAS_ID: Find this in the "Aliases" section of your agent's page. This is often TSTALIASID for the default test alias.

            Do the same for TRAINER_AGENT_ID and TRAINER_AGENT_ALIAS_ID.

Running the Server

    Activate Your Virtual Environment:

    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    Start the Flask Application:

    python app.py

API Endpoints
Health Check

    Endpoint: GET /api/health

Generate Course Plan

    Endpoint: POST /api/courses/generate

Fetch Topic Content

    Endpoint: POST /api/course/content

Generate Quiz

    Endpoint: POST /api/quiz/generate

AI Chatbot Query

    Endpoint: POST /api/chatbot/query

    Description: Takes a user's question and returns an answer from the AI assistant.

    Request Body: A JSON object with the user's question.

    Test with curl:

    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "query": "What is the difference between useEffect and useLayoutEffect in React?"
    }' \
    [http://127.0.0.1:5000/api/chatbot/query](http://127.0.0.1:5000/api/chatbot/query)

    You will receive a JSON response containing the agent's answer.

Troubleshooting
AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'

This error occurs due to a version mismatch between pyOpenSSL and its underlying cryptography dependency. To fix this, you must upgrade to the versions specified in the updated requirements.txt file.

Run the following command in your activated virtual environment to force the upgrade:

pip install --upgrade -r requirements.txt

After the installation completes, try running the application again with python app.py.
