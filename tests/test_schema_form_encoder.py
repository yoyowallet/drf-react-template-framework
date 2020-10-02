from drf_react_template.schema_form_encoder import (
    ColumnProcessor,
    SchemaProcessor,
    UiSchemaProcessor,
)
from example.polls.serializers import ChoiceListSerializer, ChoiceSerializer


def test_question_and_choice_retrieve_schema(
    choice_and_question_retrieve_expected_schema,
):
    result = SchemaProcessor(ChoiceSerializer(), {}).get_schema()
    assert result == choice_and_question_retrieve_expected_schema


def test_question_and_choice_retrieve_ui_schema(
    choice_and_question_retrieve_expected_ui_schema,
):
    result = UiSchemaProcessor(ChoiceSerializer(), {}).get_ui_schema()
    print(result)
    assert result == choice_and_question_retrieve_expected_ui_schema


def test_question_and_choice_list(choice_and_question_list_expected_schema):
    result = ColumnProcessor(ChoiceListSerializer(), {}).get_schema()
    assert result == choice_and_question_list_expected_schema
