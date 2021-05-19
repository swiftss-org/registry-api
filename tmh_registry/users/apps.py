from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "tmh_registry.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import tmh_registry.users.signals  # noqa F401 # pylint: disable=unused-import
        except ImportError:
            pass
