class AIModelError(Exception):
    def __init___(self, meassage, status_code=400, *args):
        self.message = meassage
        self.status_code = status_code
        super().__init__(self.message, *args)


class NotFoundError(Exception):
    def __init__(self, message, status_code=404, *args):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message, *args)
