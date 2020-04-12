import os
import json
import subprocess

from .CrescentApplication import CrescentApplication
from .CrescentTemplate import CrescentTemplate


class TemplateDoesNotExistError(Exception):
    def __init__(self, key):
        super().__init__('Crescent Template "{}" does not exist'.format(key))


class TemplateDoesNotHaveKeyError(Exception):
    def __init__(self, template, key):
        super().__init__(
            'Crescent Template "{}" does not have a key "{}"'.format(
                template,
                key
            )
        )


class InvalidConfigFile(Exception):
    def __init__(self, file_name):
        super().__init__('Invalid config file "{}"'.format(file_name))


class Crescent:

    def __init__(self):
        self.base_dir = self.get_config_dir()
        self.make_base_dir()

    def get_config_dir(self):
        if 'XDG_CONFIG_DIR' in os.environ.keys():
            config_dir = os.environ['XDG_CONFIG_DIR']
        else:
            try:
                config_dir = os.path.join(os.environ['HOME'], '.config')
            except KeyError:
                # TODO proper error
                raise Exception('Empty environment variable HOME')
        return os.path.join(config_dir, type(self).__name__.lower())

    def get_apps_dir(self):
        if 'XDG_DATA_HOME' in os.environ.keys():
            data_dir = os.environ['XDG_DATA_HOME']
        else:
            try:
                data_dir = os.path.join(os.environ['HOME'], '.local', 'share')
            except KeyError:
                # TODO proper error
                raise Exception('Empty environment variable HOME')
        return os.path.join(
            data_dir,
            'applications',
            type(self).__name__.lower()
        )

    def make_base_dir(self):
        try:
            os.makedirs(self.base_dir)
        except FileExistsError:
            pass

    def get_app_path(self, path):
        result = self.get_config_dir()
        if isinstance(path, str):
            return os.path.join(result, path)
        return None
        # for path in paths:
        #     result = os.path.join(result, path)
        # return result

    def get_app_json(self, file_name):
        path = self.get_app_path(file_name)
        try:
            with open(path) as f:
                content = f.read()
        except FileNotFoundError:
            content = '{}'
            with open(path, 'w+') as f:
                f.write(content)
        try:
            apps = json.loads(content)
            for app in apps:
                apps[app]['Name'] = app
            return apps
        except json.JSONDecodeError:
            raise InvalidConfigFile(file_name)

    def get_crescent_apps(self):
        apps = self.get_app_json('apps.json')
        return dict([
            (key, CrescentApplication(**apps[key])) for key in apps
        ])

    def get_crescent_templates(self):
        templates = self.get_app_json('templates.json')
        return dict([
            (key, CrescentTemplate(**templates[key])) for key in templates
        ])

    def get_apps(self):
        templates = self.get_crescent_templates()
        return [
            self.build_app_entry(app, templates)
            for app in self.get_crescent_apps().values()
        ]

    def build_app_entry(self, app, templates):
        if app.template is None:
            return app
        template = templates.get(app.template, None)
        if template is None:
            raise TemplateDoesNotExistError(app.template)
        templating_keys = app.templating
        for key in template.templating:
            if key not in app.templating:
                app.templating[key] = template.templating[key]
        for key in template.templating:
            app.keys[key] = template.templating[key].format(**templating_keys)
        for key in template.keys:
            if key not in app.keys:
                app.keys[key] = template.keys[key]
        return app

    def remove_leftovers(self, apps=None):
        apps_dir = self.get_apps_dir()
        if not apps:
            apps = self.get_apps()
        defined_apps = [app.get_filename() for app in apps]
        files = [i for i in os.listdir(apps_dir) if i.endswith('.desktop')]
        leftovers = [i for i in files if i not in defined_apps]
        for name in leftovers:
            path = os.path.join(apps_dir, name)
            # TODO logging
            print('Deleting file {}'.format(path))
            os.remove(path)

    def write_entries(self, apps=None):
        apps_dir = self.get_apps_dir()
        if not apps:
            apps = self.get_apps()
        for app in apps:
            path = os.path.join(apps_dir, app.get_filename())
            # TODO logging
            print('Writing Desktop entry {}'.format(path))
            with open(path, 'w+') as f:
                f.write(app.create_file_content())

    def update(self):
        apps = self.get_apps()
        self.remove_leftovers(apps)
        self.write_entries(apps)
        apps_dir = self.get_apps_dir()
        subprocess.run(['update-desktop-database', apps_dir])
