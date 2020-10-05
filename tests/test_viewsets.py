import pytest
from rest_framework import status

from example.polls import serializers


@pytest.mark.django_db
def test_question_and_choice_viewset_list_empty_data(
    api_client, polls_list_url, question_and_choice_list_expected_schema
):
    response = api_client.get(polls_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'serializer': question_and_choice_list_expected_schema,
        'formData': [],
    }


@pytest.mark.django_db
def test_question_and_choice_viewset_list(
    api_client, polls_list_url, question_and_choice_list_expected_schema, question
):
    response = api_client.get(polls_list_url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['serializer'] == question_and_choice_list_expected_schema
    assert response_json['formData'] == [
        {**serializers.QuestionListSerializer(question).data},
    ]
