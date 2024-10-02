from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin

from .models import ExportConfig


@admin.register(ExportConfig)
class ExportConfigModelAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    pass
