from django.apps import AppConfig


class AppaccountsConfig(AppConfig):
    name = 'appaccounts'

    def ready(self):
        import appaccounts.signals
