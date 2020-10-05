import pytest
from rest_framework.test import APIClient

from drf_react_template.schema_form_encoder import ColumnProcessor
from tests import factories


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def polls_list_url():
    return '/polls/'


@pytest.fixture
def polls_create_url(polls_list_url):
    return '/polls/create/'


@pytest.fixture
def question_and_choice_retrieve_expected_schema():
    return {
        'title': 'Question',
        'type': 'object',
        'required': ['question_text', 'pub_date'],
        'properties': {
            'question_text': {'type': 'string', 'title': 'Question Text'},
            'pub_date': {'type': 'string', 'title': 'date published'},
            'choices': {
                'title': 'Choice',
                'type': 'array',
                'minItems': 0,
                'items': {
                    'type': 'object',
                    'required': ['choice_text'],
                    'properties': {
                        'choice_text': {'type': 'string', 'title': 'Choice Text'},
                        'votes': {'type': 'integer', 'title': 'Votes', 'default': 0},
                    },
                },
            },
        },
    }


@pytest.fixture
def question_and_choice_retrieve_expected_ui_schema():
    return {
        'ui:order': ['question_text', 'pub_date', 'choices'],
        'question_text': {'ui:widget': 'textarea'},
        'pub_date': {'ui:widget': 'DatePickerWidget'},
        'choices': {
            'items': {
                'ui:order': ['choice_text', 'votes'],
                'choice_text': {'ui:widget': 'textarea'},
                'votes': {'ui:widget': 'updown'},
            }
        },
    }


@pytest.fixture
def question_and_choice_list_expected_schema():
    return [
        {
            'title': 'Question Text',
            'dataIndex': 'question_text',
            'key': 'question_text',
        },
        {'title': 'date published', 'dataIndex': 'pub_date', 'key': 'pub_date'},
    ]


@pytest.fixture
def question():
    return factories.QuestionFactory(choice=choice)


@pytest.fixture
def choice(question):
    return factories.ChoiceFactory(question=question)
