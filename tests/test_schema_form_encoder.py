from drf_react_template.schema_form_encoder import (
    ColumnProcessor,
    SchemaProcessor,
    UiSchemaProcessor,
)
from example.polls.serializers import QuestionListSerializer, QuestionSerializer


def test_question_and_choice_retrieve_schema(
    choice_and_question_retrieve_expected_schema,
):
    result = SchemaProcessor(QuestionSerializer(), {}).get_schema()
    assert result == choice_and_question_retrieve_expected_schema


def test_question_and_choice_retrieve_ui_schema(
    choice_and_question_retrieve_expected_ui_schema,
):
    result = UiSchemaProcessor(QuestionSerializer(), {}).get_ui_schema()
    assert result == choice_and_question_retrieve_expected_ui_schema


def test_question_and_choice_list(choice_and_question_list_expected_schema):
    result = ColumnProcessor(QuestionListSerializer(), {}).get_schema()
    assert result == choice_and_question_list_expected_schema
