import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import json


table_name = "ft_db"



class Field:
    
    """Encapsulates an Amazon DynamoDB table of field trial data."""
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = None

    def query_trial(self, trial_id):
        """
        :param trial_id: Trial ID
        :return: All info relate to the given trial ID.
        """
        try:
            response = self.table.query(KeyConditionExpression=Key('trial_id').eq(trial_id))
        except ClientError as err:
            logger.error(
                "Couldn't query for trial_id. Here's why: %s: %s", trial_id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Items']        