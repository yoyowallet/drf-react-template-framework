import pytest


@pytest.fixture
def choice_and_question_list_expected_schema():
    return [
        {'dataIndex': 'choice_text', 'key': 'choice_text', 'title': 'Choice Text'},
        {'dataIndex': 'votes', 'key': 'votes', 'title': 'Votes'},
    ]
