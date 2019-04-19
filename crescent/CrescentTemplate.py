from .Application import Application

class CrescentTemplate(Application):
    def __init__(self, **kwargs):
        self.templating = kwargs.pop('templating', None)
        super().__init__(**kwargs)
