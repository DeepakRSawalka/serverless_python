import os
import json
import sys
# Add the lambda_dependencies folder to the sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lambda_dependencies"))

import boto3
from google.cloud import storage
from google.oauth2 import service_account
from uuid import uuid4
import requests
from datetime import datetime, timezone

# Initialize AWS clients
sns = boto3.client('sns')
dynamodb = boto3.client('dynamodb')
# ses = boto3.client('ses', region_name=os.environ['REGION'])


def handler(event, context):

    # Initialize Google Cloud Storage client
    gcp_credentials = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    gcs_client = storage.Client(credentials=gcp_credentials)

    message = json.loads(event['Records'][0]['Sns']['Message'])
    submission_url = message['submission_url']
    email = message['email']
    user_name = message['user_name']
    user_id = message['user_id']
    assign_id = message['assign_id']

    if message['status'] == 'invalid_url': 
        status_message = 'Download Failed and Invalid submission'
        send_email(email, status_message, 'The submission URL was invalid. Please try submitting again with the correct URL.')
        log_status_to_dynamodb(str(uuid4()), email, submission_url, 'Download Failed')
        return {'statusCode': 200, 'body': json.dumps('Invalid submission handled')}

    if message['status'] == 'no_file':
        status_message = 'Download Failed and No file'
        send_email(email, status_message, 'The submission URL was invalid. Please try submitting again with the correct URL.')
        log_status_to_dynamodb(str(uuid4()), email, submission_url, 'Download Failed')
        return {'statusCode': 200, 'body': json.dumps('Invalid submission handled')}
    

    try:
        # Attempt to download the file from GitHub
        response = requests.get(submission_url)
        file_content = response.content

        # Generate a unique filename
        unique_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')
        filename = f"{user_name}_{user_id}/{assign_id}/{timestamp}_{unique_id}_{submission_url.split('/').pop()}"

        # Store in Google Cloud Storage
        bucket = gcs_client.bucket(os.environ['GCS_BUCKET_NAME'])
        blob = bucket.blob(filename)
        blob.upload_from_string(file_content)

        file_url = f"gs://{os.environ['GCS_BUCKET_NAME']}/{filename}"
        send_email(email, 'Download Successful', f'Your file has been downloaded and stored successfully. Here is the link: {file_url}')

        log_status_to_dynamodb(unique_id, email, submission_url, 'Download Successfull')

        return {'statusCode': 200, 'body': json.dumps('Process completed successfully')}
    except Exception as error:
        print('Error:', error)
        send_email(email, 'Download Failed', 'There was an error downloading your file.')
        log_status_to_dynamodb(str(uuid4()), email, submission_url, 'Download Failed')
        return {'statusCode': 500, 'body': json.dumps('Error processing your request')}

def send_email(to, subject, text):
    mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
    mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
    mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"

    response = requests.post(
        mailgun_url,
        auth=("api", mailgun_api_key),
        data={"from": "info@deepakcsye6225.me",
              "to": to,
              "subject": subject,
              "text": text}
    )

    if response.status_code == 200:
        print("Email sent successfully.")
    else:
        print("Failed to send email. Status code:", response.status_code)
      

def log_status_to_dynamodb(id, email, url, status):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE')
    table = dynamodb.Table(table_name)

    try:
        response = table.put_item(
            Item={
                'id': id,
                'Email': email,
                'SubmissionURL': url,
                'Status': status
            }
        )
        print("Log entry added to DynamoDB successfully.")
    except Exception as e:
        print(f"Failed to log to DynamoDB: {e}")
     
