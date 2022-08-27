import boto3
import json

from boto3.dynamodb.conditions import Key, Attr


table_name = "ft_db"

def get_item_count(client, table_name):
    count = client.describe_table(TableName="table_name")["Table"]["ItemCount"]
    return(count)




response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_2B'},
        # ':info': {'S': 'plot'}
    }
)
print(response['Items'])
response['Items'][1]



response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id AND begins_with ( info , :info )',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_3C'},
        ':info': {'S': 'plot'}
    },
    ReturnConsumedCapacity="Indexes"
)
print(response['Items'])




def query_trial(client, table_name, primary_key, sort_key_prefix="p"):
    response = client.query(
        TableName=table_name,
        KeyConditionExpression='trial_id = :trial_id AND begins_with ( info , :info )',
        ExpressionAttributeValues={
            ':trial_id': {'S': primary_key},
            ':info': {'S': sort_key_prefix},
        },
        # ProjectionExpression='#trt,#y',
        # ExpressionAttributeNames={
        #     "#trt":"treatment",
        #     "#y":"yield"
        # },
        PageSize=5,
        ReturnConsumedCapacity="Total"
    )
    print(response['Items'])


query_trial(client, table_name, "trial_2B", "'")






def scan_movies(self, year_range):
        """
        Scans for movies that were released in a range of years.
        Uses a projection expression to return a subset of data for each movie.

        :param year_range: The range of years to retrieve.
        :return: The list of movies released in the specified years.
        """
        yields = []
        scan_kwargs = {
            'FilterExpression': Key('year').between(year_range['first'], year_range['second']),
            'ProjectionExpression': "#yr, title, info.rating",
            'ExpressionAttributeNames': {"#yr": "year"}}
        try:
            done = False
            start_key = None
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                response = self.table.scan(**scan_kwargs)
                yields.extend(response.get('Items', []))
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as err:
            logger.error(
                "Couldn't scan for movies. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

        return yields










response = client.scan(
    TableName='ft_db',
    FilterExpression='begins_with ( info , :info )',
    # FilterExpression='info = :info',
    ExpressionAttributeValues={
        ':info': {'S': 'trt_2'},
        # ':info': {'S': 'trialmeta'},
    },
    ReturnConsumedCapacity="Total"
)
print(response['Items'])


table.scan()

response = client.scan(
    TableName='ft_db',
    FilterExpression=' yield <> :yield ',
    # FilterExpression='info = :info',
    ExpressionAttributeValues={
        ':yield': {'S': ''},
        # ':info': {'S': 'trialmeta'},
    },
    ReturnConsumedCapacity="Total"
)
print(response['Items'])




response = client.query(
    TableName='ft_db',
    KeyConditionExpression='trial_id = :trial_id',
    ExpressionAttributeValues={
        ':trial_id': {'S': 'trial_2B'},
    },
    ProjectionExpression='info',
    ReturnConsumedCapacity="Total"
)
print(response['Items'])



def scan_template(table, scan_kwargs):
    output = []
    try:
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            # response = self.table.scan(**scan_kwargs)
            response = table.scan(**scan_kwargs)
            output.extend(response.get('Items', []))
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
    except ClientError as err:
        logger.error(
            "Couldn't scan for movies. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    return output


scan_kwargs = {
    # 'FilterExpression': Key('info').begins_with("plot"),
    # 'FilterExpression': Key('info').ne("plot_0404"),
    'FilterExpression': Attr('yield').not_exists(),
    'ProjectionExpression': "trial_id, info",
    # 'ExpressionAttributeNames': {"#yr": "year"}
    "ReturnConsumedCapacity": "Total"
}

output = scan_template(table, scan_kwargs)
output

    