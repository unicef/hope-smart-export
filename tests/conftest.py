import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.hashers import make_password

if TYPE_CHECKING:
    from django.contrib.auth.models import User

here = Path(__file__).parent
DEMOAPP_PATH = here / "demoapp"
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(DEMOAPP_PATH))


def pytest_configure(config):
    os.environ.update(DJANGO_SETTINGS_MODULE="demo.settings")

    import django

    django.setup()


@pytest.fixture()
def std_user(db) -> "User":
    from demo.factories import UserFactory

    return UserFactory(
        username="admin@example.com",
        is_staff=True,
        is_active=True,
        is_superuser=False,
        password=make_password("password"),
    )
