from .Application import Application

class CrescentApplication(Application):
    def __init__(self, **kwargs):
        self.template = kwargs.pop('template', None)
        self.templating = kwargs.pop('templating', None)
        super().__init__(**kwargs)
