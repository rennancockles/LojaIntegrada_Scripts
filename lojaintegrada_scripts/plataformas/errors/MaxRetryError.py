class MaxRetryError(Exception):
    def __init__(self, e: Exception):
        super().__init__(f"Max Retry Exceeded: {e}")
