import os
import boto3
import logging

logger = logging.getLogger()

def get_connection_string():
    secret_name = os.environ['DB_CONNECTION_SECRET']
    region_name = os.environ['AWS_REGION']

    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        db_connection_string = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise e
    
    logger.info("Successfully retrieved DB connection string from Secrets Manager")

    secret = db_connection_string['SecretString']
    return secret