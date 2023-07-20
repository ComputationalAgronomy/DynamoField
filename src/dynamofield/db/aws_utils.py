import urllib.parse

import boto3


def list_all_regions():
    s = boto3.Session()
    regions = s.get_available_regions("dynamodb")
    regions.append("local")
    return regions


def get_endpoint(region):
    if region == "local":
        endpoint = "http://localhost:8000"
    else:
        ep = boto3.client("dynamodb", region_name=region).meta.endpoint_url
        endpoint = urllib.parse.urlparse(ep).hostname
    return endpoint


# import botocore.loaders
# loader = botocore.loaders.create_loader()
# data = loader.load_data("endpoints")
# resolver = botocore.regions.EndpointResolver(data)
# endpoint_data = resolver.construct_endpoint("dynamodb", "us-east-1")

