from django.apps import AppConfig


class DemoDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demo_data'
    verbose_name = 'Demo Data Management'
