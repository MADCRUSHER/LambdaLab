# LambdaLab — AWS Lambda Simulator

BCSE355L Cloud Architecture Design Digital Assignment 3.

## Core AWS Lambda simulation
- Create functions, choose runtime and trigger
- Invoke with JSON event payload
- Simulated success/failure
- Execution duration and memory output
- Invocation logs

## Meaningful enhancement
**Lambda Performance Intelligence** adds observability beyond basic invocation: invocation count, success rate, failures, average runtime, runtime history and execution logs, inspired by the Lambda + CloudWatch monitoring workflow.

## AWS coupling
The AWS Architecture page demonstrates: **Client → API Gateway → Lambda → CloudWatch**, with IAM shown as the permissions layer. This is an educational local simulation; no AWS credentials or real resources are used.

## Run locally
Double-click `run-local.bat`, or run `python -m http.server 5500` and open http://localhost:5500.

Deployment configuration is included but no deployment has been performed.
