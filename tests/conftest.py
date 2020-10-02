import pytest
from rest_framework.test import APIClient


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
                'pub_date': {'ui:widget': 'date-time'},
            }
        },
    }


@pytest.fixture
def choice_and_question_list_expected_schema():
    return [
        {'dataIndex': 'choice_text', 'key': 'choice_text', 'title': 'Choice Text'},
        {'dataIndex': 'votes', 'key': 'votes', 'title': 'Votes'},
    ]
