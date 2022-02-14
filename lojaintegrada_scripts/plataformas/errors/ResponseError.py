from requests.models import Response


class ResponseError(Exception):
    def __init__(self, response: Response):
        super().__init__(response.text)

        self.status_code = response.status_code
        self.reason = response.reason
        self.text = response.text

    def __str__(self):
        text = f"{self.status_code} {self.reason}"
        if self.text:
            text += " - {self.text}"
        return text
