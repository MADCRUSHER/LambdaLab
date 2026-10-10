import json
import os
import time
from datetime import datetime, timedelta, timezone

import boto3

cloudwatch = boto3.client("cloudwatch")
logs = boto3.client("logs")
FUNCTION_NAME = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "LambdaLab-CalculateOrderTotal")


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
        },
        "body": json.dumps(body),
    }


def calculate_order_total(payload):
    price = float(payload.get("price", 0))
    quantity = int(payload.get("quantity", 1))
    tax_rate = float(payload.get("taxRate", 0.18))
    discount = float(payload.get("discount", 0))

    if price < 0 or quantity < 1 or discount < 0:
        raise ValueError("price must be non-negative, quantity must be at least 1, and discount cannot be negative")

    subtotal = price * quantity
    discounted = max(0, subtotal - discount)
    tax = discounted * tax_rate
    total = discounted + tax

    return {
        "status": "processed",
        "currency": "INR",
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
    }


def analytics():
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=3)
    dimensions = [{"Name": "FunctionName", "Value": FUNCTION_NAME}]

    def metric(name, stat):
        result = cloudwatch.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName=name,
            Dimensions=dimensions,
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=[stat],
        )
        points = sorted(result.get("Datapoints", []), key=lambda x: x["Timestamp"])
        return points

    inv = metric("Invocations", "Sum")
    err = metric("Errors", "Sum")
    dur = metric("Duration", "Average")

    invocations = sum(p.get("Sum", 0) for p in inv)
    errors = sum(p.get("Sum", 0) for p in err)
    durations = [p.get("Average", 0) for p in dur]
    avg_duration = round(sum(durations) / len(durations), 2) if durations else 0
    success_rate = round(((invocations - errors) / invocations) * 100, 2) if invocations else 0

    recent_logs = []
    try:
        log_result = logs.filter_log_events(
            logGroupName=f"/aws/lambda/{FUNCTION_NAME}",
            startTime=int(start.timestamp() * 1000),
            endTime=int(end.timestamp() * 1000),
            limit=20,
        )
        for item in log_result.get("events", [])[-10:]:
            recent_logs.append({
                "timestamp": item.get("timestamp"),
                "message": item.get("message", "").strip(),
            })
    except Exception as exc:
        recent_logs = [{"message": f"CloudWatch log query unavailable: {exc}"}]

    return {
        "source": "Amazon CloudWatch",
        "functionName": FUNCTION_NAME,
        "window": "last 3 hours",
        "invocations": int(invocations),
        "errors": int(errors),
        "successRate": success_rate,
        "averageDurationMs": avg_duration,
        "durationDatapoints": [
            {"timestamp": p["Timestamp"].isoformat(), "averageMs": round(p.get("Average", 0), 2)}
            for p in dur
        ],
        "logs": recent_logs,
    }


def handler(event, context):
    path = event.get("rawPath") or event.get("path") or "/"
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    print(json.dumps({"event": "request", "path": path, "method": method}))

    if path == "/health":
        return response(200, {"status": "ok", "service": "AWS Lambda", "function": FUNCTION_NAME})

    if path == "/functions" and method == "GET":
        return response(200, {
            "functions": [{
                "name": FUNCTION_NAME,
                "runtime": "Python 3.12",
                "trigger": "Amazon API Gateway",
                "status": "ACTIVE",
            }]
        })

    if path == "/analytics" and method == "GET":
        return response(200, analytics())

    if path == "/invoke" and method == "POST":
        try:
            raw = event.get("body") or "{}"
            payload = json.loads(raw) if isinstance(raw, str) else raw
            started = time.perf_counter()
            result = calculate_order_total(payload)
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            print(json.dumps({"event": "calculation_success", "durationMs": elapsed, "result": result}))
            return response(200, {
                "success": True,
                "function": FUNCTION_NAME,
                "runtime": "Python 3.12",
                "durationMs": elapsed,
                "result": result,
            })
        except Exception as exc:
            print(json.dumps({"event": "calculation_error", "error": str(exc)}))
            return response(400, {
                "success": False,
                "function": FUNCTION_NAME,
                "error": str(exc),
            })

    return response(404, {"error": "Route not found"})
