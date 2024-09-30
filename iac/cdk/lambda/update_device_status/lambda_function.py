import boto3

def lambda_handler(event, context):
    actionGroup = event['actionGroup']
    function = event['function']
    print("event", event)
    
    param_dict = {p['name']: p['value'] for p in event['parameters']}
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    # Get the device name from the event
    device_name = param_dict['id']
    new_status = param_dict['status']
    
    # Update the device status in DynamoDB
    try:
        response = dynamodb.update_item(
            TableName='sample-devices',
            Key={
                'id': {'S': device_name}
            },
            UpdateExpression='SET #status = :new_status',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':new_status': {'S': new_status}
            },
            ReturnValues='UPDATED_NEW'
        )
        
        print(f"Updated device '{device_name}' status to '{new_status}'")
        responseBody =  {
            "TEXT": {
                "body": "The function {} was called successfully!".format(function)
            }
        }
    except Exception as e:
        print(f"Error updating device '{device_name}' status: {e}")
        responseBody =  {
            "TEXT": {
                "body": f"Error updating device '{device_name}' status: {e}"
            }
        }
        
    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }
    
    return {
        'response': action_response, 
        'messageVersion': event['messageVersion']
    }