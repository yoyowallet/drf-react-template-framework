from drf_react_template.schema_form_encoder import (
    ColumnProcessor,
    SchemaProcessor,
    UiSchemaProcessor,
)
from example.polls.serializers import QuestionListSerializer, QuestionSerializer


def test_question_and_choice_retrieve_schema(
    question_and_choice_context,
    question_and_choice_retrieve_expected_schema,
):
    result = SchemaProcessor(
        QuestionSerializer(), question_and_choice_context
    ).get_schema()
    assert result == question_and_choice_retrieve_expected_schema


def test_question_and_choice_retrieve_ui_schema(
    question_and_choice_context,
    question_and_choice_retrieve_expected_ui_schema,
):
    result = UiSchemaProcessor(
        QuestionSerializer(), question_and_choice_context
    ).get_ui_schema()
    assert result == question_and_choice_retrieve_expected_ui_schema


def test_question_and_choice_list(question_and_choice_list_expected_schema):
    result = ColumnProcessor(QuestionListSerializer(), {}).get_schema()
    assert result == question_and_choice_list_expected_schema
