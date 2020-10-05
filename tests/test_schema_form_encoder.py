import pytest
from rest_framework import serializers

from drf_react_template.schema_form_encoder import (
    ColumnProcessor,
    SchemaProcessor,
    UiSchemaProcessor,
)
from example.polls.serializers import (
    ChoiceSerializer,
    QuestionListSerializer,
    QuestionSerializer,
)


def test_question_and_choice_retrieve_schema(
    question_and_choice_retrieve_expected_schema,
):
    result = SchemaProcessor(QuestionSerializer(), {}).get_schema()
    assert result == question_and_choice_retrieve_expected_schema


def test_question_and_choice_retrieve_ui_schema(
    question_and_choice_retrieve_expected_ui_schema,
):
    result = UiSchemaProcessor(QuestionSerializer(), {}).get_ui_schema()
    assert result == question_and_choice_retrieve_expected_ui_schema


def test_question_and_choice_list(question_and_choice_list_expected_schema):
    result = ColumnProcessor(QuestionListSerializer(), {}).get_schema()
    assert result == question_and_choice_list_expected_schema


def test_choice_custom_widget_and_type():
    new_widget = 'CustomWidget'
    new_type = 'CustomType'

    class CustomWidgetSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(
            style={'ui:widget': new_widget, 'schema:type': new_type}
        )

    result = SchemaProcessor(CustomWidgetSerializer(), {}).get_schema()
    assert result['properties']['choice_text']['type'] == new_type

    result = UiSchemaProcessor(CustomWidgetSerializer(), {}).get_ui_schema()
    assert result['choice_text']['ui:widget'] == new_widget


def test_question_list_sort():
    order = 'ascend'

    class QuestionListSortSerializer(QuestionListSerializer):
        pub_date = serializers.DateField(style={'schema:sort': order})

    result = ColumnProcessor(QuestionListSortSerializer(), {}).get_schema()
    assert result[1]['defaultSortOrder'] == order


def test_question_list_sort_bad_key():
    order = 'BAD_KEY'

    class QuestionListSortSerializer(QuestionListSerializer):
        pub_date = serializers.DateField(style={'schema:sort': order})

    with pytest.raises(ValueError):
        ColumnProcessor(QuestionListSortSerializer(), {}).get_schema()
