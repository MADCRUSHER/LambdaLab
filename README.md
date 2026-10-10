# LambdaLab — Real AWS Connected Version

BCSE355L Cloud Architecture Design — Digital Assignment 3.

This version keeps the original Lambda simulator UI but adds a real AWS serverless backend:

- Amazon API Gateway HTTP API
- AWS Lambda (Python 3.12)
- Amazon CloudWatch Metrics
- Amazon CloudWatch Logs
- IAM execution permissions generated through AWS SAM
- Custom enhancement: Lambda Performance Intelligence dashboard

## Architecture

Browser → API Gateway → Lambda → CloudWatch

The browser never contains AWS access keys. Only the API Gateway URL is placed in `config.js`.

## Deploy to AWS

### Prerequisites

1. AWS account
2. AWS CLI configured (`aws configure`)
3. AWS SAM CLI installed
4. A region such as `ap-south-1` (Mumbai)

### Option A — Windows

Open `aws/deploy.bat` and run it.

Or from PowerShell:

```powershell
cd aws
sam build
sam deploy --guided
```

Recommended answers during guided deployment:

- Stack name: `lambdalab-aws`
- Region: `ap-south-1`
- Allow SAM to create IAM roles: `Y`
- Confirm changes before deploy: `Y`

At the end SAM prints an `ApiUrl` similar to:

`https://abc123.execute-api.ap-south-1.amazonaws.com`

Copy that URL into `config.js`:

```js
window.AWS_CONFIG = {
  apiBaseUrl: "https://abc123.execute-api.ap-south-1.amazonaws.com"
};
```

Then open the website again.

## Test the real AWS connection

Health check:

```text
GET <ApiUrl>/health
```

Functions:

```text
GET <ApiUrl>/functions
```

Invoke Lambda:

```text
POST <ApiUrl>/invoke
Content-Type: application/json

{
  "price": 100,
  "quantity": 3,
  "taxRate": 0.18,
  "discount": 20
}
```

Analytics:

```text
GET <ApiUrl>/analytics
```

The analytics endpoint reads AWS Lambda metrics and CloudWatch log events through the Lambda execution role.

## Demo flow

1. Open the website.
2. Click **Load Demo**.
3. Go to **Invoke**.
4. Send an order JSON payload.
5. Show the result saying **REAL AWS LAMBDA EXECUTION**.
6. Open **AWS Architecture** and explain Browser → API Gateway → Lambda → CloudWatch.
7. Open **Analytics** and show real CloudWatch invocation/error/duration data.
8. Explain the enhancement: the project turns raw Lambda observability into a simple performance dashboard.

## Security

Never put `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` into `index.html`, `script.js`, `config.js`, or any frontend file. The frontend only knows the API Gateway URL. AWS credentials stay in your AWS CLI environment/IAM setup.

## Cleanup

When the assignment is finished, delete the CloudFormation/SAM stack if you no longer need it:

```powershell
aws cloudformation delete-stack --stack-name lambdalab-aws --region ap-south-1
```

This removes the AWS resources created by the stack.
