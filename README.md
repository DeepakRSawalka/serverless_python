## Serverless - Event Driven Architecture

# This project contains a serverless Lambda function that is triggered by Amazon Simple Notification Service (SNS) to manage software releases. Upon invocation, it performs three primary actions:

- **Download**: Fetches the latest release from a specified GitHub repository and stores in GCP Storage Account.
- **Notification**: Sends an email to the user about the status of the download.
- **Logging**: Records the email activity in an Amazon DynamoDB table for tracking.

## Prerequisites

- AWS account with access to Lambda, SNS, and DynamoDB services.
- Google Cloud account with access to Google Cloud Storage.
- GitHub account with access to the repository containing releases.
- `aws-cli` and `gcloud` CLI tools installed and configured on your machine.