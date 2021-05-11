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
def polls_create_url(polls_list_url):
    return '/polls/create/'


@pytest.fixture
def question():
    return factories.QuestionFactory(choice=choice)


@pytest.fixture
def choice(question):
    return factories.ChoiceFactory(question=question)


@pytest.fixture
def question_and_choice_retrieve_expected_schema():
    return {
        'title': 'Question',
        'type': 'object',
        'required': ['question_text', 'pub_date'],
        'properties': {
            'question_text': {'type': 'string', 'title': 'Question text'},
            'pub_date': {'type': 'string', 'title': 'date published'},
            'choices': {
                'title': 'Choices',
                'type': 'array',
                'minItems': 0,
                'items': {
                    'type': 'object',
                    'required': ['choice_text'],
                    'properties': {
                        'choice_text': {'type': 'string', 'title': 'Choice text'},
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
            'title': 'Question text',
            'dataIndex': 'question_text',
            'key': 'question_text',
        },
        {'title': 'date published', 'dataIndex': 'pub_date', 'key': 'pub_date'},
    ]


@pytest.fixture
def choice_conditional_dependency_votes():
    return {
        'properties': {'votes': {'default': 0, 'title': 'Votes', 'type': 'integer'}},
        'required': ['votes'],
    }


@pytest.fixture
def choice_dynamic_dependency_votes():
    return {
        'choice_text': {
            'oneOf': [
                {
                    'properties': {
                        'choice_text': {
                            'type': 'string',
                            'title': 'Choice text',
                            'enum': ['yes'],
                            'enumNames': ['Yes'],
                        },
                        'votes': {'type': 'integer', 'title': 'Votes'},
                    },
                    'required': ['votes'],
                },
                {
                    'properties': {
                        'choice_text': {
                            'type': 'string',
                            'title': 'Choice text',
                            'enum': ['no'],
                            'enumNames': ['No'],
                        }
                    },
                    'required': [],
                },
            ]
        }
    }


@pytest.fixture
def custom_field_type_expected_schema():
    return {
        'choice_text': {
            'type': 'string',
            'title': 'Choice text'
        },
        'votes': {
            'type': 'integer',
            'title': 'Votes',
            'default': 0
        },
        'image_field': {
            'type': 'file',
            'title': 'Image field'
        },
        'uuid_field': {
            'type': 'uuid',
            'title': 'Uuid field'
        }
    }
