import pytest
from demo.factories import user_grant_permission
from django.urls import reverse

pytestmark = [pytest.mark.admin]


@pytest.fixture()
def cfg():
    from demo.factories import ConfigurationFactory

    return ConfigurationFactory(columns="id", data={"field_separator": ","})


def test_changelist(django_app, std_user, cfg):
    url = reverse("admin:hope_smart_export_configuration_changelist")

    with user_grant_permission(std_user, ["hope_smart_export.view_configuration"]):
        assert std_user.has_perm("hope_smart_export.view_configuration")
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200


def test_change(django_app, std_user, cfg):
    url = reverse("admin:hope_smart_export_configuration_change", args=(cfg.id,))
    with user_grant_permission(std_user, ["hope_smart_export.change_configuration"]):
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200


def test_add(django_app, std_user, cfg):
    url = reverse("admin:hope_smart_export_configuration_add")
    with user_grant_permission(std_user, ["hope_smart_export.add_configuration"]):
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200


def test_test(django_app, std_user, cfg):
    url = reverse("admin:hope_smart_export_configuration_change", args=(cfg.id,))
    with user_grant_permission(std_user, ["hope_smart_export.change_configuration"]):
        res = django_app.get(url, user=std_user)
        res = res.click("Test")
        res.forms["action-form"]["max_records"] = "-1"
        res = res.forms["action-form"].submit(expect_errors=True)
        assert res.status_code == 400
        res.forms["action-form"]["max_records"] = "10"
        res = res.forms["action-form"].submit()
        assert res.status_code == 200


def test_configure(django_app, std_user, cfg):
    url = reverse("admin:hope_smart_export_configuration_change", args=(cfg.id,))
    with user_grant_permission(std_user, ["hope_smart_export.change_configuration"]):
        res = django_app.get(url, user=std_user)
        res = res.click("Configure")
        res = res.forms["config-form"].submit(expect_errors=True)
        assert res.status_code == 400
        res.forms["config-form"]["field_separator"] = ";"
        res = res.forms["config-form"].submit()
        assert res.status_code == 302
