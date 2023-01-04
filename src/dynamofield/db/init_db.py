import os
import shlex
import subprocess
import boto3
import botocore
import botocore.exceptions
import requests
import tarfile 

def init_db_table(client, table_name):
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
        TableName=table_name,
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

def remove_table(client, table_name):
    try:
        client.delete_table(TableName=table_name)
    except botocore.exceptions.ClientError as e:
        print(f"Table does NOT exist: {table_name}. Error: {e}")
    


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

