from aws_cdk import (
    aws_lambda as _lambda,
    Duration
)

from constructs import Construct

class ActionGroupLambda(Construct):
    def __init__(self, scope: Construct, id:str = "LambdaStack", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the Lambda function resource
        self.action_func = _lambda.Function(
            self,
            "BedrockVoiceAgentActionLambda",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset("cdk/lambda/update_device_status"), # Points to the lambda directory
            handler = "lambda_function.lambda_handler",
            timeout = Duration.minutes(3),   
        )