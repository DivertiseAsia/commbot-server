from django.apps import AppConfig


class CommManagerConfig(AppConfig):
    name = "comm_manager"
    verbose_name = "Comm Manager"

    def ready(self):
        import comm_manager.signals
