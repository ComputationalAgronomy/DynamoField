import os
import shlex
import subprocess
import boto3
import botocore
import botocore.exceptions
import psutil
import requests
import tarfile


def add_db_table(client, tablename):
    try:
        response = client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'field_trial_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'record_type',
                    'AttributeType': 'S'
                }
            ],
            TableName=tablename,
            KeySchema=[
                {
                    'AttributeName': 'field_trial_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'record_type',
                    'KeyType': 'RANGE'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            },
        )
        response = f"New table created: {tablename}."
    except botocore.exceptions.ClientError as e:
        response = f"Table already exist Tablename: {tablename}. {e}"
    print(response)
    return response


def remove_table(client, tablename):
    try:
        response = client.delete_table(TableName=tablename)
        response = f"Successfully delete table: {tablename}."
    except botocore.exceptions.ClientError as e:
        response = (f"Table does NOT exist: {tablename}. Error: {e}")
        print(response)
    return response


def delete_all_items_sort_key(client: botocore.client, tablename, sort_key):
    print(f"tablename:{tablename}\tsort_key:{sort_key}")
    try:
        response = client.scan(
            TableName=tablename,
            FilterExpression='begins_with ( record_type , :record_type )',
            ExpressionAttributeValues={
                ':record_type': {'S': f"{sort_key}_"},
            },
            ProjectionExpression='field_trial_id, record_type',
        )
        # print(response['Items'])
        for k in response['Items']:
            # print(k)
            client.delete_item(TableName=f"{tablename}", Key=k)
        len_data = len(response['Items'])
        response = f"Successfully delete {len_data} items from record_type: {sort_key}. table:{tablename}."
    except botocore.exceptions.ClientError as e:
        response = (f"Error delete_item in sort_key: {tablename}."
                    f"sort_key: {sort_key}. Error: {e}")
        print(response)
    return response


def start_dynamodb_server(path=".", jar="DynamoDBLocal.jar", lib="DynamoDBLocal_lib"):
    jar = os.path.join(path, jar)
    lib = os.path.join(path, lib)
    command = f"java -Djava.library.path={lib} -jar {jar} -sharedDb &"
    command_line = shlex.split(command)
    _ = subprocess.run(command, shell=True)


def test_local_dynamodb():
    # allp = [p.info["cmdline"] for p in psutil.process_iter(["cmdline"])]
    useful_info = ["cmdline", "pid", "name", "cwd", "exe"]
    java_proc = [p.info for p in psutil.process_iter(useful_info) if "python3" in p.info["cmdline"]]
    # cmd = java_proc[0]["cmdline"]
    db_exist = [search_dynamodblocal(proc["cmdline"]) for proc in java_proc]
    any_java_db = any(db_exist)
    return any_java_db


def search_dynamodblocal(cmd):
    is_jar = any(["DynamoDBLocal.jar" in i for i in cmd])
    is_lib = any(["DynamoDBLocal_lib" in i for i in cmd])
    is_shared = any(["-sharedDb" in i for i in cmd])
    return is_jar #+is_lib

