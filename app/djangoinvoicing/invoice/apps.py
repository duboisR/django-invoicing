from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class invoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice'
    verbose_name = _("Module de facturation")
