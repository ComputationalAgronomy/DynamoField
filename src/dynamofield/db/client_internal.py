import boto3


def delete_all_items(client, table_name):
    # KeyConditionExpression='field_trial_id = :field_trial_id AND begins_with( record_type, :record_type)',
    # response = client.query(
    #     TableName='ft_db',
    #     FilterExpression='begins_with(field_trial_id, :trial_id)',
    #     # KeyConditionExpression='field_trial_id = :trial_id',
    #     FilterExpression='begins_with ( record_type , :record_type )',
    #     ExpressionAttributeValues={
    #         # ':field_trial_id': {'S': 'trial_3C'},
    #         ':record_type': {'S': 'plot_01'},
    #     },
    #     ProjectionExpression='field_trial_id, record_type',
    # )
    # print(response['Items'])
    response = client.scan(
        TableName=table_name,
        FilterExpression='begins_with ( field_trial_id , :field_trial_id )',
        # FilterExpression='record_type = :record_type',
        ExpressionAttributeValues={
            ':field_trial_id': {'S': 'trial_'},
            # ':record_type': {'S': 'trialmeta'},
        },
        ProjectionExpression='field_trial_id, record_type',
        ReturnConsumedCapacity="Total",
    )
    for k in response['Items']:
        client.delete_item(TableName="ft_db", Key=k)



def delete_by_sort_key(client, table_name, sort_key):
    # KeyConditionExpression='field_trial_id = :field_trial_id AND begins_with( record_type, :record_type)',
    # response = client.query(
    response = client.scan(
        TableName=table_name,
        # FilterExpression='begins_with(trial_id, :trial_id)',
        # KeyConditionExpression='trial_id = :trial_id',
        FilterExpression='begins_with ( record_type , :record_type )',
        ExpressionAttributeValues={
            # ':field_trial_id': {'S': 'trial_3C'},
            ':record_type': {'S': f"{sort_key}_"},
        },
        ProjectionExpression='field_trial_id, record_type',
    )
    # print(response['Items'])
    # response = client.scan(
    #     TableName=table_name,
    #     FilterExpression='begins_with ( field_trial_id , :field_trial_id )',
    #     FilterExpression='record_type = :record_type',
    #     ExpressionAttributeValues={
    #         ':field_trial_id': {'S': 'trial_'},
    #         # ':record_type': {'S': 'trialmeta'},
    #     },
    #     ProjectionExpression='field_trial_id, record_type',
    #     ReturnConsumedCapacity="Total",
    # )
    # print(response['Items'])
    for k in response['Items']:
        # print(k)
        client.delete_item(TableName="ft_db", Key=k)
