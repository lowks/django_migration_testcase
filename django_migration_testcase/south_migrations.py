from south.migration import Migrations

from .base import BaseMigrationTestCase


class MigrationTest(BaseMigrationTestCase):
    """Test for migrations, reworked from:
    https://micknelson.wordpress.com/2013/03/01/testing-django-migrations/

    """

    def setUp(self):
        super(MigrationTest, self).setUp()

        self.before_migrations = []
        for app_name, version in self.before:
            migrations = Migrations(app_name)
            self.before_migrations.append((app_name, migrations.guess_migration(
                self._get_migration_number(version)).name()))
        self.after_migrations = []
        for app_name, version in self.after:
            migrations = Migrations(app_name)
            self.after_migrations.append((app_name, migrations.guess_migration(
                self._get_migration_number(version)).name()))

        self.before_orm = {}
        for app_name, version in self.before_migrations:
            migrations = Migrations(app_name)
            self.before_orm[app_name] = migrations[version].orm()
        self.after_orm = {}
        for app_name, version in self.after_migrations:
            migrations = Migrations(app_name)
            self.after_orm[app_name] = migrations[version].orm()

        for app_name, version in self.before_migrations:
            # Do a fake migration first to update the migration history.
            self.migrate(app_name, version=None, fake=True)
            self.migrate(app_name, version=version)

    def _get_model(self, model_name, orm_dict):
        app_name, model_name = self._get_app_and_model_name(model_name)
        # Because we store all the orms for each migration against
        # their app name, lookup the relevant orm state first.
        orm = orm_dict[app_name]
        model_name = '{app_name}.{model_name}'.format(
            app_name=app_name,
            model_name=model_name)
        return orm[model_name]

    def get_model_before(self, model_name):
        self._check_migration_not_run()
        return self._get_model(model_name, self.before_orm)

    def get_model_after(self, model_name):
        self._check_migration_run()
        return self._get_model(model_name, self.after_orm)

    def run_migration(self):
        for app_name, version in self.after_migrations:
            self.migrate(app_name, version)
        self._migration_run = True

    def _get_migration_number(self, migration_name):
        # TODO: make this better and report exception
        return migration_name.split('_')[0]
