class Archive:
    def __init__(
        self,
        host=None,
        access_key=None,
        secret_key=None,
        compliancy_bucket=None,
    ):
        self.host = host if host is not None else "localhost:9000"
        self.access_key = access_key if access_key is not None else "admin"
        self.secret_key = secret_key if secret_key is not None else "?"
        self.compliancy_bucket = (
            compliancy_bucket if compliancy_bucket is not None else "compliancy-bucket"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.access_key} \
{self.secret_key} {self.compliancy_bucket}"


class Destination:
    def __init__(
        self,
        host=None,
        token=None,
    ):
        self.host = host if host is not None else "localhost:8088"
        self.token = token if token is not None else "aa-bb"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.token}"

    def url(self) -> str:
        return f"https://{self.host}/services/collector/event"

    def headers(self) -> dict:
        return {"Authorization": "Splunk " + self.token}
