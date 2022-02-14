class APIError(Exception):
    def __init__(self, api_response):
        self.code = api_response.get("code", "")
        self.message = api_response.get("message", "")
        self.response = api_response

        super().__init__(f"API Error: {self.message}")
