import pytest
from rest_framework.test import APIClient

from tests import factories


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def polls_list_url():
    return '/polls/'


@pytest.fixture
def choice_and_question_retrieve_expected_schema():
    return {
        'title': 'Choice',
        'type': 'object',
        'required': ['choice_text'],
        'properties': {
            'choice_text': {'type': 'string', 'title': 'Choice Text'},
            'votes': {'type': 'integer', 'title': 'Votes', 'default': 0},
            'questions': {
                'title': 'Questions',
                'type': 'array',
                'minItems': 0,
                'items': {
                    'type': 'object',
                    'required': ['question_text', 'pub_date'],
                    'properties': {
                        'question_text': {'type': 'string', 'title': 'Question Text'},
                        'pub_date': {'type': 'string', 'title': 'date published'},
                    },
                },
            },
        },
    }


@pytest.fixture
def choice_and_question_retrieve_expected_ui_schema():
    return {
        'ui:order': ('choice_text', 'votes', 'questions'),
        'choice_text': {},
        'votes': {'ui:widget': 'updown'},
        'questions': {
            'items': {
                'ui:order': ('question_text', 'pub_date'),
                'question_text': {},
                'pub_date': {'ui:widget': 'date'},
            }
        },
    }


@pytest.fixture
def choice_and_question_list_expected_schema():
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
