# crypto.py
import boto3
import json
from cryptography.fernet import Fernet
from botocore.exceptions import ClientError


class Crypto:
    def __init__(self, secret_name, region_name):
        self.secret_name = secret_name
        self.region_name = region_name

    def get_key(self):
        session = boto3.session.Session()
        client = session.client(
            aws_access_key_id="your-aws-access-key-id",
            aws_secret_access_key="your-aws-secret-access-key",
            service_name="secretsmanager",
            region_name=self.region_name,
        )
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            raise Exception("Couldn't retrieve the secret key") from e
        secret = get_secret_value_response["SecretString"]
        secret = json.loads(secret)
        return secret["connector_fernet_key"]

    def encrypt(self, data: str) -> str:
        """
        Encrypt the provided data using the key from Secrets Manager.
        """
        key = self.get_key()
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypt the provided data using the key from Secrets Manager.
        """
        key = self.get_key()
        fernet = Fernet(key)
        return fernet.decrypt(data.encode()).decode()
