from django.apps import AppConfig


class DemoManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demo_manager'
    verbose_name = 'Demo Manager'

    def ready(self):
        import demo_manager.signals
