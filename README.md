# dialog_management

A platform for managing user dialog with AI

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Architecture

![Architecture](https://github.com/lyoudr/dialogue/blob/main/architecture.png)

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up ENV

- Create .env file in root dir

```
DATABASE_URL=$DB_URL
OPENAI_API_KEY=$OPENAI_API_KEY
GCP_PROJECT_ID=$GCP_PROJECT_ID
```

- Authenticate to GCP

```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service_account.json
```

### Install required pacakges

```
pip install -r requirements/local.txt
```

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

- You can create another user in /admin page

### Type checks

Running type checks with mypy:

    $ mypy dialogmanagement

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

### Running tests with pytest

    $ pytest

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd dialogmanagement
celery -A config.celery_app worker -l info
```

### Redis

Start Redis Server as Broker.

```bash
redis-server
```

### DataBase

- Run Migration

```
python manage.py migrate
```

- Load required initial data

```
python manage.py loaddata dialogmanagement/ai_model/fixtures/model_fixture.json
python manage.py loaddata dialogmanagement/ai_model/fixtures/model_version_fixture.json
```

### Start Server

```
python manage.py runserver 0.0.0.0:8000
```

### API Docs

`http://127.0.0.1:8000/api/docs/`

## Models

![Models](https://github.com/lyoudr/dialogue/blob/main/schema.png)

### User

- Original Django User to allow each user login.

### AIModel

- name: Define used model : (CHATGPT, GEMINI)

### ModelVersion

- ai_model: Foreign Key to **AIModel**
- name: model version for used model, ex: "gpt-4o" or "gemini-2.0-flash"

### Dialogue

- user: Foreign Key to original **User**
- status: During chat with LLM, status is ACTIVE. After finish , status is COMPLETED
- content: text content.
- type: Define it is AI response or user question.
- model = Foregin Key to **AIModel**
- model_version = Foreign Key to **model_version**

## APIs

- Authentication :
  - `POST` `/api/auth-token/` Type username and password to get token, and then use the token to do authentication
- Authorization :
  - Need to use `/admin` page to add required permissions ("dialogue.view_dialogue", "dialogue.add_dialogue") to user
  - Use `DialoguePermission` in `/dialogmanagement/dialogue/ai/views.py` to do authorization
- AIModel:
  - `GET` `/api/aimodel/` Get current available ai model
  - `GET` `/api/modelversion/` Get current available ai model version
- Dialogue:
  - `GET` `/api/dialogue/` Get current user dialogue history
  - `POST` `/api/dialogue/` Create dialogue with selected model, and model version
  - `GET` `/api/dialogue/{id}` Get specific dialogue by id
  - `POST` `/api/dialogue/search-dialogue/` Full-text search `Dialogue` `content` field by input `keyword`, and return related dialogues
    - Remember to modify request body to
      ```
      {
        "keyword": "Hello"
      }
      ```
  - `PUT` `/api/dialogue/update-dialogue` Update dialogue history, which means you can only see the following dialogue after updating

## Asynchronous Tasks

- Use `Celery/Redis` to handle chating with LLM asynchronously

## Code Scalability

- Apply **Factory Mode** in `dialogmanagement/utils/ai_service.py` to allow user to chat with different LLM

## Modify Dialogue

- Login in to `http://127.0.0.1:8000/admin`, and enter to page `http://127.0.0.1:8000/admin/dialogue/dialogue/`
- You can update dialogue history here.
