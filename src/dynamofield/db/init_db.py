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
                    'AttributeName': 'trial_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'info',
                    'AttributeType': 'S'
                }
            ],
            TableName=tablename,
            KeySchema=[
                {
                    'AttributeName': 'trial_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'info',
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
    


def download_dynamodb_jar(dy_path="."):
    URL = "https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"
    DOWNLOAD_NAME = "dynamodb_local_latest.tar.gz"
    # dy_path = "dynamodb"
    os.makedirs(dy_path, exist_ok=True)
    outfile = os.path.join(dy_path, DOWNLOAD_NAME)
    response = requests.get(URL)
    with open(outfile, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1048576): #8192
            f.write(chunk)
    with tarfile.open(outfile, "r:gz") as tar:
        tar.extractall(path=dy_path)



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

