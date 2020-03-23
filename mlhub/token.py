from typing import Dict, Tuple, Optional


class Tokens:
    def __init__(self) -> None:
        self.token: Optional[str] = None
        self.aws_access_key: Optional[str] = None
        self.aws_secret_key: Optional[str] = None

    def add_access_token(self, token: str) -> None:
        self.token = token
        print("Added token!")

    def add_aws_credentials(self, aws_access_key: str, aws_secret_key: str) -> None:
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        print("Added AWS credentials!")

    def get_token(self) -> str:
        if self.token is None:
            raise AssertionError("Token must be set to use package")
        return self.token

    def get_aws_credentials(self) -> Tuple[str, str]:
        if (self.aws_access_key is None) or (self.aws_secret_key is None):
            raise AssertionError("AWS credentials must be set to use package")
        return self.aws_access_key, self.aws_secret_key


token_class = Tokens()


def set_token(token: str) -> None:
    token_class.add_access_token(token)


def set_aws_credentials(aws_access_key: str, aws_secret_key: str) -> None:

    token_class.add_aws_credentials(aws_access_key, aws_secret_key)


def get_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token_class.get_token()}",
        "Accept": "application/json",
    }


def get_credentials() -> Tuple[str, str]:
    return token_class.get_aws_credentials()
