class CustomValidator:
    message = None
    code = None
    is_custom = True

    def __init__(self, code=None, message=None):
        self.code = code or self.code
        self.message = message or self.message

        if self.code is None:
            raise NotImplementedError('A validation code must be provided.')
        if self.message is None:
            raise NotImplementedError('A validation message must be provided.')

        def __call__(self, value):
            raise NotImplementedError('A __call__ method must be provided.')

