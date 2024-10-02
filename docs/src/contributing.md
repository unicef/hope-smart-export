# Contributing


Install [uv](https://docs.astral.sh/uv/)


    git clone ..
    uv venv .venv --python 3.12
    source .venv/bin/activate
    uv sync --extra docs


## Run tests
    pytests tests


## Run demo app

    tests/demoapp/manage.py migrate

    tests/demoapp/manage.py runserver

!!! note 

    You can login in the demo application as superuser using any username/password
