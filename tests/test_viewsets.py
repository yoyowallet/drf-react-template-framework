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


@pytest.mark.django_db
def test_question_and_choice_viewset_create(
    api_client,
    polls_create_url,
    question_and_choice_retrieve_expected_schema,
    question_and_choice_retrieve_expected_ui_schema,
):
    response = api_client.get(polls_create_url)

    assert response.status_code == status.HTTP_200_OK
    response_obj = response.json()
    assert (
        response_obj['serializer']['schema']
        == question_and_choice_retrieve_expected_schema
    )
    assert (
        response_obj['serializer']['uiSchema']
        == question_and_choice_retrieve_expected_ui_schema
    )

    import pprint
    pprint.pprint(response_obj)
