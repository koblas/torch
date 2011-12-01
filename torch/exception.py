class TorchError(Exception):
    def __init__(self, message):
        super(TorchError, self).__init__("TorchError: %s" % message)

class ConnectionError(TorchError):
    pass

class ResponseError(TorchError):
    pass

class ResponseError(TorchError):
    pass
