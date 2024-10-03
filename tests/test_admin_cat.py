import pytest
from demo.factories import user_grant_permission
from django.urls import reverse

pytestmark = [pytest.mark.admin]


@pytest.fixture()
def category():
    from demo.factories import CategoryFactory

    return CategoryFactory()


def test_changelist(django_app, std_user, category):
    url = reverse("admin:hope_smart_export_category_changelist")

    with user_grant_permission(std_user, ["hope_smart_export.view_category"]):
        assert std_user.has_perm("hope_smart_export.view_category")
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200


def test_change(django_app, std_user, category):
    url = reverse("admin:hope_smart_export_category_change", args=(category.id,))
    with user_grant_permission(std_user, ["hope_smart_export.change_category"]):
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200


def test_add(django_app, std_user, category):
    url = reverse("admin:hope_smart_export_category_add")
    with user_grant_permission(std_user, ["hope_smart_export.add_category"]):
        res = django_app.get(url, user=std_user)
    assert res.status_code == 200
