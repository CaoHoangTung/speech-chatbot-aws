import random
from aws_cdk import (
    CfnOutput,
    aws_iam as iam,
    aws_bedrock as bedrock,
    aws_lambda as _lambda,
    Duration
)
from constructs import Construct
from cdk.constructs.prompt_templates import orchestration_template
import os
import json

class BedrockVoiceAgentConstruct(Construct):
    def __init__(self, 
        scope: Construct, 
        id: str,
        dynamodb_table: Construct,
        bedrock_agent_action_func: Construct,
        agent_foundational_model: str,
        **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        dynamodb_table.table.grant_read_write_data(bedrock_agent_action_func)

        agent_role = iam.Role(self, "BedrockVoiceAgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "BedrockVoiceAgentPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            resources=[bedrock_agent_action_func.function_arn],
                        )
                    ]
                ),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )

        # Generate a random prefix
        prefix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))

        cfn_agent = bedrock.CfnAgent(self, "BedrockVoiceAgent", 
            agent_name="bedrock-voice-agent-" + prefix,
            agent_resource_role_arn=agent_role.role_arn,
            instruction="You are a helpful agent with strong analytics skills.",
            foundation_model=agent_foundational_model,
            auto_prepare=True,
            action_groups=[bedrock.CfnAgent.AgentActionGroupProperty(
                action_group_name="update-device-state",
                action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                    lambda_=bedrock_agent_action_func.function_arn
                ),
                function_schema=bedrock.CfnAgent.FunctionSchemaProperty(
                    functions=[bedrock.CfnAgent.FunctionProperty(
                        name="update-device-status",
                        description="Update the status of a device",
                        parameters={
                            "id": bedrock.CfnAgent.ParameterDetailProperty(
                                type="string",
                                description="the name of the device",
                                required=True
                            ),
                            "status": bedrock.CfnAgent.ParameterDetailProperty(
                                type="string",
                                description="the updated status of the device",
                                required=True
                            )
                        }
                    )]
                )
            )],
            # knowledge_bases=[bedrock.CfnAgent.AgentKnowledgeBaseProperty(
            #     description="The knowledge base for the BedrockVoice Agent",
            #     knowledge_base_id=self.knowledge_base.attr_knowledge_base_id,
            # )],
            prompt_override_configuration=bedrock.CfnAgent.PromptOverrideConfigurationProperty(
                prompt_configurations=[
                    bedrock.CfnAgent.PromptConfigurationProperty(
                        base_prompt_template = json.dumps(orchestration_template),
                        inference_configuration=bedrock.CfnAgent.InferenceConfigurationProperty(
                            maximum_length=2048,
                            stop_sequences=["</invoke>", "</answer>", "</error>"],
                            temperature=0,
                            top_k=250,
                            top_p=1
                        ),
                        prompt_creation_mode="OVERRIDDEN",
                        prompt_type="ORCHESTRATION"
                    )
                ]
            )
        )

        # Add bedrock invokation permission
        bedrock_agent_action_func.add_permission(
            "AllowBedrockInvocation",
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=cfn_agent.attr_agent_arn,
        )

        cfn_agent_alias = bedrock.CfnAgentAlias(self, "BedrockVoiceAgentAlias",
            agent_alias_name="bedrock_voice_agent_alias",
            agent_id=cfn_agent.attr_agent_id,
        )

        self.agent_id = cfn_agent.attr_agent_id
        self.agent_alias_id = cfn_agent_alias.attr_agent_alias_id