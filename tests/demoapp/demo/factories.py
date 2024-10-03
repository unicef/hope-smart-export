from typing import Any, Optional

import factory
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory
from factory.faker import Faker
from strategy_field.utils import fqn

from hope_smart_export.exporters import ExportAsText
from hope_smart_export.models import Configuration, Category


class CategoryFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Category {n}")

    class Meta:
        model = Category
        django_get_or_create = ["name"]


class ConfigurationFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Config {n}")
    code = factory.Sequence(lambda n: f"code-{n}")
    content_type = factory.Iterator(ContentType.objects.all())
    exporter = fqn(ExportAsText)

    class Meta:
        model = Configuration

    @factory.post_generation  # type: ignore[misc]
    def categories(self, create: bool, extracted: list[str], **kwargs: Any) -> None:
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for name in extracted:
                self.categories.add(CategoryFactory(name=name))


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"email{n}@example.com")

    class Meta:
        model = User


class GroupFactory(DjangoModelFactory):
    name = Faker("name")

    class Meta:
        model = Group
        django_get_or_create = ("name",)

    @factory.post_generation  # type: ignore[misc]
    def permissions(self, create: bool, extracted: list[str], **kwargs: Any) -> None:
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for perm_name in extracted:
                app, perm = perm_name.split(".")
                self.permissions.add(Permission.objects.get(content_type__app_label=app, codename=perm))


class user_grant_permission:
    def __init__(self, user: User, permissions: Optional[list[str]] = None):
        self.user = user
        self.permissions = permissions
        self.group = None

    def __enter__(self):
        if hasattr(self.user, "_group_perm_cache"):
            del self.user._group_perm_cache
        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache
        self.group = GroupFactory(permissions=self.permissions or [])
        self.user.groups.add(self.group)

    def __exit__(self, *exc_info):
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()

    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self):
        """Stop an active patch."""
        return self.__exit__()
