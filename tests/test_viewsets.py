import pytest
from rest_framework import status


@pytest.mark.django_db
def test_question_and_choice_viewset_list_empty_data(
    api_client, polls_list_url, choice_and_question_list_expected_schema
):
    response = api_client.get(polls_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'serializer': choice_and_question_list_expected_schema,
        'formData': [],
    }
