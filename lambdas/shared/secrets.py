import os
import boto3
import logging

logger = logging.getLogger()

def get_connection_string():
    parameter_name = os.environ['DB_CONNECTION_PARAMETER']
    region_name = os.environ['AWS_REGION']

    client = boto3.client("ssm", region_name=region_name)

    try:
        response = client.get_parameter(Name=parameter_name, WithDecryption=True)
    except Exception as e:
        logger.error(f"Error retrieving parameter: {e}")
        raise e

    logger.info("Successfully retrieved DB connection string from SSM Parameter Store")
    return response['Parameter']['Value']
