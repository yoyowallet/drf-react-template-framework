import pytest
from rest_framework.test import APIClient

from example.polls.viewsets import PollViewSet


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def polls_list_url():
    return '/polls/'


@pytest.fixture
def choice_and_question_list_expected_schema():
    return [
        {'dataIndex': 'choice_text', 'key': 'choice_text', 'title': 'Choice Text'},
        {'dataIndex': 'votes', 'key': 'votes', 'title': 'Votes'},
    ]
