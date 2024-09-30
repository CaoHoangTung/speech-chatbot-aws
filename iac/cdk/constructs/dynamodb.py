from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    custom_resources as cr
)

from constructs import Construct

ITEMS = [
    {
        "id": {"S": "living room light"},
        "status": {"S": "off"},
    },
    {
        "id": {"S": "living room air conditioner"},
        "status": {"S": "off"},
    },
    {
        "id": {"S": "bedroom air conditioner"},
        "status": {"S": "off"},
    },
    {
        "id": {"S": "bedroom light"},
        "status": {"S": "off"},
    },
    {
        "id": {"S": "bathroom light"},
        "status": {"S": "off"},
    }
]

class DynamoDBTable(Construct):
    def create_dynamodb_item(self, table, table_name, item):
        cr.AwsCustomResource(self, f"dynamodb-initial-data-{item.get('id')}",
            on_create=cr.AwsSdkCall(
                service="DynamoDB",
                action="putItem",
                parameters={
                    "TableName": table.table_name,
                    "Item": item,
                },
                physical_resource_id=cr.PhysicalResourceId.of(f"{table_name}_initialization")
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

    def __init__(self, scope: Construct, id:str = "DDBStack", table_name="sample-devices", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.table = dynamodb.Table(
            self,
            "BedrockVoiceDynamoDBTable",
            table_name=table_name,
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        for item in ITEMS:
            self.create_dynamodb_item(self.table, table_name, item)