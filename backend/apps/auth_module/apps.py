from django.apps import AppConfig


class AuthModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth_module"

    def ready(self):
        import apps.auth_module.signals  # noqa: F401
