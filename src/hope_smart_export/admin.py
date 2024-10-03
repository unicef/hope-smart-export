from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import AdminForm
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse

from .models import Category, Configuration


class ExportTestForm(forms.Form):
    max_records = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], initial=10)
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all())


@admin.register(Category)
class CategoryModelAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Configuration)
class ExportConfigModelAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "code", "content_type")
    list_filter = ("content_type", "categories")
    search_fields = ("name", "code")
    exclude = ("data",)
    filter_horizontal = ("categories",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type")

    def get_changeform_initial_data(self, request):
        return {"columns": "id\n"}

    @button(visible=lambda o: o.context["original"].pk)
    def configure(self, request, pk: str) -> TemplateResponse | HttpResponseRedirect:
        ctx = self.get_common_context(request, pk)
        obj: Configuration = ctx["original"]
        form_class = obj.exporter.config_class
        status_code = 200
        if request.method == "POST":
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                obj.data = form.cleaned_data
                obj.save()
                self.message_user(request, "Configuration saved")
                return HttpResponseRedirect("..")
            status_code = 400
        else:
            form = form_class()
        fs = (("", {"fields": form_class.declared_fields}),)
        ctx["admin_form"] = AdminForm(form, fs, {})  # type: ignore[arg-type]

        ctx["form"] = form
        return TemplateResponse(request, "admin/hope_smart_export/configure.html", ctx, status=status_code)

    @button()
    def test(self, request, pk: str) -> TemplateResponse | HttpResponse:
        ctx = self.get_common_context(request, pk)
        configuration: Configuration = ctx["original"]
        status_code = 200
        if request.method == "POST":
            form = ExportTestForm(request.POST, request.FILES)
            if form.is_valid():
                qs = form.cleaned_data["content_type"].model_class().objects.all()[: form.cleaned_data["max_records"]]
                output = configuration.export(qs)
                return HttpResponse(output, content_type="text/plain")
            status_code = 400
        else:
            form = ExportTestForm(initial={"content_type": configuration.content_type})
        ctx["form"] = form
        return TemplateResponse(request, "admin/hope_smart_export/test.html", ctx, status=status_code)
