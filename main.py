import os
import json
import boto3
from google.cloud import storage
from uuid import uuid4
import requests

# Initialize AWS clients
sns = boto3.client('sns')
dynamodb = boto3.client('dynamodb')
ses = boto3.client('ses', region_name=os.environ['AWS_REGION'])

# Initialize Google Cloud Storage client
gcp_credentials = json.loads(os.environ['GOOGLE_CREDENTIALS'])
gcs_client = storage.Client(credentials=gcp_credentials)

def handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    submission_url = message['submission_url']
    email = message['email']
    user_name = message['user_name']
    user_id = message['user_id']
    assign_id = message['assign_id']

    if message['status'] in ['invalid_url', 'no_file']:
        status_message = 'Download Failed and Invalid submission' if message['status'] == 'invalid_url' else 'Download Failed and No file'
        send_email(email, status_message, 'The submission URL was invalid. Please try submitting again with the correct URL.')
        log_status_to_dynamodb(str(uuid4()), email, submission_url, 'Download Failed')
        return {'statusCode': 200, 'body': json.dumps('Invalid submission handled')}

    try:
        # Attempt to download the file from GitHub
        response = requests.get(submission_url)
        file_content = response.content

        # Generate a unique filename
        unique_id = str(uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f"{user_name}_{user_id}/{assign_id}/{timestamp}_{unique_id}_{submission_url.split('/').pop()}"

        # Store in Google Cloud Storage
        bucket = gcs_client.bucket(os.environ['GCS_BUCKET_NAME'])
        blob = bucket.blob(filename)
        blob.upload_from_string(file_content)

        file_url = f"gs://{os.environ['GCS_BUCKET_NAME']}/{filename}"
        send_email(email, 'Download Successful', f'Your file has been downloaded and stored successfully. Here is the link: {file_url}')

        log_status_to_dynamodb(unique_id, email, submission_url, 'Download Successful')

        return {'statusCode': 200, 'body': json.dumps('Process completed successfully')}
    except Exception as error:
        print('Error:', error)
        send_email(email, 'Download Failed', 'There was an error downloading your file.')
        log_status_to_dynamodb(str(uuid4()), email, submission_url, 'Download Failed')
        return {'statusCode': 500, 'body': json.dumps('Error processing your request')}

def send_email(to, subject, text):
    pass
      

def log_status_to_dynamodb(id, email, url, status):
    pass
     
