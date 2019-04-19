from enum import Enum

class ApplicationKeyError(Exception):
    def __init__(self, key, msg='Invalid key "{}"'):
        super().__init__(msg.format(key))

class ApplicationKeyTypeError(ApplicationKeyError):
    def __init__(self, key):
        super().__init__(key, msg='Invalid key type for "{}"')

class ApplicationUnknownKeyError(ApplicationKeyError):
    def __init__(self, key):
        super().__init__(key, msg='Non-standard key "{}"')

class ApplicationMissingRequiredKeyError(ApplicationKeyError):
    def __init__(self, key):
        super().__init__(key, msg='Missing required key "{}"')

class Application:
    class Type(Enum):
        APPLICATION = 'Application'
        LINK = 'Link'
        DIRECTORY = 'Directory'

    VERISON = 1.1
    LEGAL_KEYS = {
        'Type': Type,
        'Name': str,
        'GenericName': str,
        'NoDisplay': bool,
        'Comment': str,
        'Icon': str,
        'Hidden': bool,
        'OnlyShowIn': list,
        'NotShowIn': list,
        'DBusActivatable': bool,
        'TryExec': str,
        'Exec': str,
        'Path': str,
        'Terminal': bool,
        'MimeType': list,
        'Categories': list,
        'Implements': list,
        'Keywords': list,
        'StartupNotify': bool,
        'StartupWMClass': str,
    }
    REQUIRED_KEYS = [
        'Name',
    ]

    @staticmethod
    def sanitize_filename(name):
        return ''.join(c if c.isalnum() else '_' for c in name)

    @staticmethod
    def convert_value(value):
        if isinstance(value, str):
            return value
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, list):
            return ';'.join(value)
        if isinstance(value, bool):
            return str(value).lower()
        return value

    def __init__(self, **kwargs):
        self.keys = {}
        self.keys['Type'] = Application.Type.APPLICATION.value
        for key in Application.REQUIRED_KEYS:
            try:
                value = kwargs.pop(key)
                if not isinstance(value, Application.LEGAL_KEYS[key]):
                    raise ApplicationKeyTypeError(key)
                self.keys[key] = value
            except KeyError:
                raise ApplicationMissingRequiredKeyError(key)
        for key in kwargs:
            if not key in Application.LEGAL_KEYS:
                raise ApplicationUnknownKeyError(key)
            if not isinstance(kwargs[key], Application.LEGAL_KEYS[key]):
                raise ApplicationKeyTypeError(key)
            self.keys[key] = kwargs[key]

    def get_filename(self):
        return '{}.desktop'.format(
            Application.sanitize_filename(self.keys['Name'])
        )

    def create_file_content(self):
        result = []
        result.append('[Desktop Entry]')
        for key, value in self.keys.items():
            result.append('{key}={value}'.format(
                key=key,
                value=Application.convert_value(value))
            )
        return '\n'.join(result)

    def __str__(self):
        msg = '[{}]'.format(self.keys['Name'])
        keys = []
        for key in Application.LEGAL_KEYS:
            if key in self.keys:
                keys.append(key)
        if keys:
            msg += ' ' + ', '.join([
                '{key}={value}'.format(key=key, value=self.keys[key]) for \
                key in self.keys
            ])
        return msg

    def __repr__(self):
        return '<Desktop Application: {}>'.format(self.__str__())
