import boto3
from boto3.dynamodb.conditions import Key

def get_item(table_name: str, primary_key_name: str, key: str) -> dict:
    table = boto3.resource("dynamodb").Table(table_name)
    response = table.get_item(Key={primary_key_name: key})
    if "Item" not in response:
        return None
    return response["Item"]

def get_all_items(table_name: str) -> list[dict]:
    table = boto3.resource("dynamodb").Table(table_name)
    response = table.scan()
    return response['Items']

def put_item(table_name: str, item: dict) -> None:
    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item=item)

def update_item(table_name: str, primary_key_name: str, key: str, update_attributes: dict) -> dict:
    item = get_item(table_name, primary_key_name, key)
    item.update(update_attributes)
    put_item(table_name, item)
    return item
    

def delete_item(table_name: str, primary_key_name: str, key: str) -> None:
    table = boto3.resource("dynamodb").Table(table_name)
    table.delete_item(Key={primary_key_name: key})

def get_all_items_by_index(table_name: str, index_key: str, key_value: str) -> list[dict]:
    """
    Query items by an index, assuming the index name matches the index key.

    :param table_name: Name of the DynamoDB table
    :param index_key: The key for the GSI and also the index name
    :param key_value: Value of the key to query
    :return: List of items matching the query
    """
    table = boto3.resource("dynamodb").Table(table_name)
    response = table.query(
        IndexName=index_key,
        KeyConditionExpression=Key(index_key).eq(key_value)
    )
    return response['Items']

def delete_all_items_by_index(table_name: str, index_key: str, key: str) -> None:
    """
    Delete all items by an index, assuming the index name matches the index key.

    :param table_name: Name of the DynamoDB table
    :param index_key: The key for the GSI and also the index name
    :param key: Value of the key to query
    """
    items = get_all_items_by_index(table_name, index_key, key)
    for item in items:
        delete_item(table_name, index_key, item[index_key])
