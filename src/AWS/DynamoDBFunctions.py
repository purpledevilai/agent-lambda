import boto3

def get_item(table_name: str, primary_key_name:str,  key: str) -> dict:
    table = boto3.resource("dynamodb").Table(table_name)
    response = table.get_item(Key={primary_key_name: key})
    return response["Item"]

def get_all_items(table_name: str) -> list[dict]:
    table = boto3.resource("dynamodb").Table(table_name)
    response = table.scan()
    return response['Items']

def put_item(table_name: str, item: dict) -> None:
    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item=item)

def delete_item(table_name: str, primary_key_name: str, key: str) -> None:
    table = boto3.resource("dynamodb").Table(table_name)
    table.delete_item(Key={primary_key_name: key})