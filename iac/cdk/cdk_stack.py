from aws_cdk import (
    CfnParameter,
    Stack,
)
from constructs import Construct
from cdk.constructs.agent import BedrockVoiceAgentConstruct
from cdk.constructs.dynamodb import DynamoDBTable
from cdk.constructs.action_lambda_function import ActionGroupLambda

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.agent_foundational_model = CfnParameter(self, "AgentFoundationalModel",
            type="String",
            default="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        # The code that defines your stack goes here

        self.dynamodb_table = DynamoDBTable(self)
        self.action_group_lambda = ActionGroupLambda(self)

        self.agent = BedrockVoiceAgentConstruct(
            self,
            id="BedrockVoiceAgentConstruct",
            dynamodb_table=self.dynamodb_table,
            bedrock_agent_action_func=self.action_group_lambda.action_func,
            agent_foundational_model=self.agent_foundational_model.value_as_string,
        )