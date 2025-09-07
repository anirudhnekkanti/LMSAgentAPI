import boto3
import os
import uuid
import json

# --- AWS Bedrock Agent Configuration ---

# Ensure your AWS credentials are configured (e.g., via AWS CLI `aws configure`)
# and the following environment variables are set in your .env file.
COURSE_CREATOR_AGENT_ID = os.getenv("COURSE_CREATOR_AGENT_ID")
COURSE_CREATOR_AGENT_ALIAS_ID = os.getenv("COURSE_CREATOR_AGENT_ALIAS_ID")
TRAINER_AGENT_ID = os.getenv("TRAINER_AGENT_ID")
TRAINER_AGENT_ALIAS_ID = os.getenv("TRAINER_AGENT_ALIAS_ID")
AWS_REGION = os.getenv("AWS_REGION_NAME", "us-east-1") # Default to us-east-1 if not set

# Create a Bedrock Agent Runtime client
try:
    bedrock_agent_runtime = boto3.client(
        'bedrock-agent-runtime',
        region_name=AWS_REGION
    )
except Exception as e:
    print(f"Error creating Boto3 client: {e}")
    bedrock_agent_runtime = None


def _invoke_agent(agent_id, agent_alias_id, prompt):
    """
    A helper function to invoke a Bedrock agent and parse the streaming response.
    """
    if not bedrock_agent_runtime:
        raise Exception("Boto3 client is not initialized. Check AWS credentials and region.")

    if not all([agent_id, agent_alias_id]):
        raise Exception("Agent ID and/or Agent Alias ID are not configured in .env file.")

    # A unique session ID is required for each conversation with the agent
    session_id = str(uuid.uuid4())

    try:
        # The invoke_agent call sends the prompt to the agent and gets a streaming response
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt
        )

        # The response 'completion' is a streaming body. We need to iterate
        # through the chunks to assemble the final response.
        response_text = ""
        for event in response.get('completion', []):
            chunk = event.get('chunk', {})
            if 'bytes' in chunk:
                response_text += chunk['bytes'].decode('utf-8')
        
        if not response_text:
            raise Exception("Agent returned an empty response.")
            
        print(f"Raw agent response: {response_text}")
        
        # The agent's response is expected to be a JSON string.
        return json.loads(response_text)

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: Failed to parse agent response. Raw response was: {response_text}")
        raise Exception(f"Agent returned a malformed JSON: {e}")
    except Exception as e:
        print(f"Error during agent invocation: {e}")
        raise e


def invoke_course_creator_agent(prompt):
    """
    Invokes the CourseCreatorAgent on AWS Bedrock.
    """
    return _invoke_agent(COURSE_CREATOR_AGENT_ID, COURSE_CREATOR_AGENT_ALIAS_ID, prompt)


def invoke_trainer_agent(prompt):
    """
    Invokes the TrainerAgent on AWS Bedrock to get content for a topic.
    """
    return _invoke_agent(TRAINER_AGENT_ID, TRAINER_AGENT_ALIAS_ID, prompt)

