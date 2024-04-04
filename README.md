## Serverless - Event Driven Architecture

**This project contains a serverless Lambda function that is triggered by Amazon Simple Notification Service (SNS) to manage software releases. Upon invocation, it performs three primary actions:**

- **Download**: Fetches the latest release from a specified GitHub repository and stores in Google Cloud Storage Bucket.
- **Notification**: Sends an email to the user about the status of the download - whether successful or encountered an issue.
- **Logging**: To maintain a comprehensive record of the operations and facilitate easy tracking of activities, the function logs each email notification sent into an Amazon DynamoDB table.

## Prerequisites

- AWS account with access to Lambda, SNS, and DynamoDB services.
- Google Cloud account with access to Google Cloud Storage.
- A URL to a GitHub release that is available publicly and provided in a zip format.
- `aws-cli` and `gcloud` CLI tools installed and configured on your machine.

## Setup and Installation

**Step 1** : Clone the Repository
```bash
git clone git@github.com:DeepakSawalka/serverless_python.git
```
**Step 2** : Create Virtual Environment inside the folder
```bash
python3 -m venv .venv
```
**Step 3** : Activate Virtual Environment in cmd.exe 
```bash
.\venv\Scripts\activate.bat
```
**Step 4** : Install dependencies from requirements.txt file
```bash
pip install -r requirements.txt
```
## Deploy to AWS Lambda

 - To deploy the Lambda function on AWS, this project utilizes Pulumi for infrastructure provisioning and management

 ## Verify your Deployment

 - After deployment, use the Pulumi console or AWS Management Console to verify that your Lambda function and associated resources are correctly configured and operational.