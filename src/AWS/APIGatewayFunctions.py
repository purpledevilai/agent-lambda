import json
import decimal

# Dumb thing to handle decimal types
def default_type_error_handler(obj):
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    raise Exception(f"Object of type {type(obj)} with value of {repr(obj)} is not JSON serializable")

def create_api_gateway_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Allow requests from any origin
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",  # Allow these headers
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"  # Allow specific methods
        },
        "body": json.dumps(body, default=default_type_error_handler)
    }
