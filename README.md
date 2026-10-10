# LambdaLab — AWS Serverless Order Processing & Performance Analytics

> **BCSE355L — Cloud Architecture Design | Digital Assignment 3**

LambdaLab is a web-based lab for exploring an AWS Lambda workflow through a clean dashboard. It combines an interactive frontend with a **deployed AWS serverless backend**, allowing users to submit order data, execute real Lambda invocations, and inspect operational analytics.

**GitHub:** https://github.com/MADCRUSHER/LambdaLab

## Highlights

- **Real serverless execution:** Submit an order payload through Amazon API Gateway and invoke an AWS Lambda function running Python 3.12.
- **Order-total calculation:** Calculate subtotal, discount, tax, and final total from a JSON request.
- **Performance Intelligence dashboard:** Present invocation counts, error counts, success rate, execution-duration history, and logs.
- **AWS observability:** Use Amazon CloudWatch metrics and logs to help understand the deployed function's behaviour.
- **Infrastructure as code:** Build and deploy the backend with AWS Serverless Application Model (AWS SAM).
- **Credential-free frontend:** The browser uses the API Gateway URL; AWS credentials should remain in your local AWS CLI/IAM environment.

## Architecture

```text
┌───────────────┐      HTTPS       ┌──────────────────┐
│   Web Browser │ ───────────────▶ │ Amazon API       │
│  HTML/CSS/JS  │                  │ Gateway (HTTP API)│
└───────────────┘                  └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │   AWS Lambda     │
                                   │   Python 3.12    │
                                   └────────┬─────────┘
                                            │
                         ┌──────────────────┴──────────────────┐
                         ▼                                     ▼
                ┌──────────────────┐                  ┌──────────────────┐
                │ CloudWatch Metrics│                  │ CloudWatch Logs  │
                └──────────────────┘                  └──────────────────┘

              IAM execution permissions are defined through AWS SAM
```

### Request flow

1. The user enters an order payload in the browser.
2. The frontend sends an HTTPS request to the API Gateway endpoint.
3. API Gateway invokes the deployed Lambda function.
4. Lambda calculates the order total and returns a JSON response.
5. CloudWatch provides operational metrics and logs for monitoring and debugging.

## Technology stack

| Layer | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| API | Amazon API Gateway HTTP API |
| Compute | AWS Lambda, Python 3.12 |
| Monitoring | Amazon CloudWatch Metrics and Logs |
| Permissions | AWS IAM execution role |
| Deployment | AWS SAM, AWS CLI |
| Assignment | BCSE355L Cloud Architecture Design — DA-3 |

## Project structure

```text
LambdaLab/
├── index.html
├── style.css
├── script.js
├── config.js                 # API Gateway URL for the frontend
├── package.json
├── run-local.bat
├── vercel.json
├── README.md
└── aws/
    ├── template.yaml         # SAM infrastructure definition
    ├── deploy.bat
    ├── samconfig.toml.example
    └── src/
        ├── app.py            # Lambda handler
        └── requirements.txt
```

## Run the frontend locally

### 1. Clone the repository

```bash
git clone https://github.com/MADCRUSHER/LambdaLab.git
cd LambdaLab
```

### 2. Configure the API URL

Open `config.js` and set `apiBaseUrl` to the `ApiUrl` output from your own SAM deployment.

```javascript
window.AWS_CONFIG = {
  apiBaseUrl: "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com"
};
```

If you are using the already-deployed demo backend, use the API URL configured by the project maintainer. The endpoint is public, so avoid sending private or sensitive data.

### 3. Start a local web server

From the project root, run:

```powershell
python -m http.server 5500
```

Then open <http://localhost:5500> in your browser.

Alternatively, on Windows, use `run-local.bat` if it is configured for your environment.

> Opening `index.html` directly as a `file://` URL may cause browser restrictions. Serving it over localhost is recommended.

## Deploy the AWS backend

### Prerequisites

- An AWS account with permission to create the required resources
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.12 available for the SAM build
- A target AWS region, such as `ap-south-1` (Mumbai)

### Option A — Windows deployment script

From the repository root, run:

```powershell
.\aws\deploy.bat
```

### Option B — AWS SAM commands

```powershell
cd aws
sam build
sam deploy --guided
```

During guided deployment, choose a stack name and AWS region, and review the IAM permissions and resource changes before confirming. Save the deployment configuration locally if desired; do **not** commit a real `samconfig.toml` if it contains environment-specific settings or sensitive values.

After deployment, SAM prints an `ApiUrl` output. Copy that URL into `config.js`:

```javascript
window.AWS_CONFIG = {
  apiBaseUrl: "https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com"
};
```

Restart or refresh the local frontend after updating the configuration.

## API endpoints

Replace `<ApiUrl>` with the base URL returned by SAM.

### Health check

```http
GET <ApiUrl>/health
```

Checks whether the backend is responding.

### Functions

```http
GET <ApiUrl>/functions
```

Lists the functions exposed by the backend, if enabled in the deployed template.

### Invoke the order calculator

```http
POST <ApiUrl>/invoke
Content-Type: application/json
```

Example request:

```json
{
  "price": 100,
  "quantity": 3,
  "taxRate": 0.18,
  "discount": 20
}
```

Example calculation:

- Subtotal: `100 × 3 = ₹300.00`
- Discount: `₹20.00`
- Tax: `18% × (₹300.00 − ₹20.00) = ₹50.40`
- **Total: ₹330.40**

The actual response includes the calculated result and execution metadata. Exact response fields depend on the deployed handler version.

### Analytics

```http
GET <ApiUrl>/analytics
```

Returns analytics used by the dashboard, subject to the deployed handler's implementation and IAM permissions.

## Demo walkthrough

1. Start the frontend and open it in a browser.
2. Load the demo payload or enter the sample order above.
3. Open **Invoke** and submit the request.
4. Show the successful response from the deployed AWS Lambda backend.
5. Open **AWS Architecture** and explain the browser → API Gateway → Lambda flow.
6. Open **Analytics** and explain the displayed invocation, error, duration, and log information.
7. Describe the enhancement: **Lambda Performance Intelligence** turns operational information into a dashboard that is easier to interpret during a demonstration.

For the AWS console walkthrough, open the Lambda function and its **Monitor** section, then inspect the associated CloudWatch logs and metrics.

## Security and cost notes

- **Never** put `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, session tokens, or other credentials in frontend files.
- `config.js` contains an API endpoint, not an AWS credential. However, a public API URL can be called by anyone who obtains it.
- The deployed demo API currently has no authentication. Do not send personal, confidential, or production data to it. For a public production deployment, add appropriate authorization, throttling, validation, and abuse protections.
- AWS resources can incur charges. Review AWS pricing and monitor usage while the stack is deployed.
- Keep local environment-specific configuration and secrets out of Git.

## Remove the AWS deployment

When you no longer need the stack, delete the **actual stack name used during deployment**. For example, if the stack is named `lambdalab`:

```powershell
aws cloudformation delete-stack --stack-name lambdalab --region ap-south-1
```

Check the stack name and region before running the command. Deleting the stack removes resources managed by that CloudFormation stack; verify the AWS console afterward for any resources that remain.

## Learning outcomes

LambdaLab demonstrates a practical serverless workflow: API-based invocation, event-driven compute, infrastructure as code, IAM execution permissions, and monitoring with CloudWatch. The Performance Intelligence dashboard adds an application-level view of operational behaviour to support testing, troubleshooting, and explanation of the architecture.
