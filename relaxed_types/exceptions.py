class ReturnTypeError(TypeError):

    def __init__(self, msg, value):
        super(ReturnTypeError, self).__init__(msg)
        self.value = value
