import boto3


def delete_all_items(client, table_name):
    # KeyConditionExpression='trial_id = :trial_id AND begins_with( info, :info)',
    # response = client.query(
    #     TableName='ft_db',
    #     FilterExpression='begins_with(trial_id, :trial_id)',
    #     # KeyConditionExpression='trial_id = :trial_id',
    #     FilterExpression='begins_with ( info , :info )',
    #     ExpressionAttributeValues={
    #         # ':trial_id': {'S': 'trial_3C'},
    #         ':info': {'S': 'plot_01'},
    #     },
    #     ProjectionExpression='trial_id, info',
    # )
    # print(response['Items'])
    response = client.scan(
        TableName='table_name',
        FilterExpression='begins_with ( trial_id , :trial_id )',
        # FilterExpression='info = :info',
        ExpressionAttributeValues={
            ':trial_id': {'S': 'trial_'},
            # ':info': {'S': 'trialmeta'},
        },
        ProjectionExpression='trial_id, info',
        ReturnConsumedCapacity="Total",
    )
    print(response['Items'])
    for k in response['Items']:
        client.delete_item(TableName="ft_db", Key=k)
