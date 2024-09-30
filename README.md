# Speech Chatbot on AWS with Amazon Transcribe, Amazon Polly, and Amazon Bedrock

## Prerequisites
- Python 3.10
- pip

## Installation
### Deploy the base components with CDK
0. Navigate to the `iac` directory
```bash
cd iac
```

1. Bootstrap the environment
```bash
cdk bootstrap
```

2. Deploy the environment
```bash
cdk deploy
```

### Install python dependencies
```bash
pip install -r requirements.txt
```

## Run the script
```bash
export AGENT_ID={REPLACE_AGENT_ID} && export AGENT_ALIAS_ID={REPLACE_ALIAS_ID} && python main.py
```
Replace the AGENT_ID and AGENT_ALIAS_ID with the output from the cloudformation template

Speak into the mic to see the result.