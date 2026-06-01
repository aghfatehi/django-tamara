class TamaraException(Exception):
    def __init__(self, message="", errors=None, code=0, previous=None):
        super().__init__(message)
        self.errors = errors or []
        self.code = code
        self.previous = previous

    def get_errors(self):
        return self.errors
