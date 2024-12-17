import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


def dynamodb_query(table, id=''):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)

    # Scan the table with a filter to get items where 'check' is True
    response = table.scan(
        FilterExpression=Attr('id').eq(id)
    )

    # Retrieve and print the items
    items = response.get('Items', [])
    return items


def dynamo_db_update(table, item_id='', attribute='', value=''):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    try:
        # Update the item with id = '123', setting the value attribute
        response = table.update_item(
            Key={
                'id': f'{item_id}'  # Primary key of the item to update
            },
            UpdateExpression="SET #v = :new_value",
            ExpressionAttributeNames={
                "#v": f"{attribute}"  # 'value' is the attribute to update
            },
            ExpressionAttributeValues={
                ":new_value": value  # New value to set
            }
        )
        return "ok"
    except ClientError as e:
        return e.response['Error']['Message']
    except Exception as e:
        return str(e)
