
import os
import subprocess
import tarfile

import requests


# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
AWS_DB_URL = [
    "https://ad1ni2b6xgvw0s0.cloudfront.net/dynamodb_local_latest.tar.gz",
    "https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"]


def download_dynamodb(url):
    filename = url.split("/")[-1]
    try:
        response = requests.get(url)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1048576):  # 8192
                f.write(chunk)
        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall()
    except Exception:
        pass


def check_dynamodb_local():
    db_jar = "DynamoDBLocal.jar"
    if not os.path.isfile(db_jar):
        print("Setup DynamoDB Local files.")
        for url in AWS_DB_URL:
            download_dynamodb(url)
            is_exist = os.path.isfile(db_jar)
            if is_exist:
                break
    is_exist = os.path.isfile(db_jar)
    return is_exist


def check_java():
    try:
        # capture output
        _ = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        print(e)
        return False
    

if __name__ == "__main__":
    if check_java():
        print("Java is installed")
    else:
        print("Java is not installed")
    if check_dynamodb_local():
        print("DynamoDB Local is installed")
    else:
        print("DynamoDB Local is not installed")
