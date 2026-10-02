import requests


class BaseApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 10
        self.session.headers.update({"Accept": "application/json"})

    def send_request(self, method, endpoint, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self.timeout
        url = self.base_url + endpoint
        return self.session.request(method=method, url=url, **kwargs)

    def get(self, endpoint, **kwargs):
        return self.send_request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.send_request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.send_request("PUT", endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.send_request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.send_request("DELETE", endpoint, **kwargs)
