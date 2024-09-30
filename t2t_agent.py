import logging
import random
import boto3
import os
from botocore.exceptions import ClientError

REGION = "us-east-1"
AGENT_ID = os.environ["AGENT_ID"]
AGENT_ALIAS_ID = os.environ["AGENT_ALIAS_ID"]
logger = logging.getLogger(__name__)

def converse(agents_runtime_client, agent_id, agent_alias_id, session_id, prompt):
    """
    Sends a prompt for the agent to process and respond to.
    :param agent_id: The unique identifier of the agent to use.
    :param agent_alias_id: The alias of the agent to use.
    :param session_id: The unique identifier of the session. Use the same value across requests
                        to continue the same conversation.
    :param prompt: The prompt that you want Claude to complete.
    :return: Inference response from the model.
    """

    try:
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt. In some cases, it can take up to a minute or more to
        # generate a response.
        response = agents_runtime_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
        )

        completion = ""
        for event in response.get("completion"):
            chunk = event.get("chunk", "")
            completion += chunk["bytes"].decode()
        return completion
    except ClientError as e:
        logger.error(f"Couldn't invoke agent. {e}")
        return f"Couldn't invoke agent. {e}"

if __name__ == "__main__":
    agents_runtime_client = boto3.client('bedrock-agent-runtime', region_name=REGION)
    response = converse(
        agents_runtime_client, 
        AGENT_ID, 
        AGENT_ALIAS_ID, 
        "session"+str(random.randint(1,100000)), 
        "Turn off the bathroom lightbulb"
    )
    print(response)