from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RegistryConfig(AppConfig):
    name = "tmh_registry.registry"
    verbose_name = _("Registry")

    def ready(self):
        try:
            import tmh_registry.registry.signals  # noqa F401 # pylint: disable=unused-import
        except ImportError:
            pass
