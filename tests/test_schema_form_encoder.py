from drf_react_template.schema_form_encoder import ColumnProcessor
from tests.test_examples.choice_and_question.serializers import ChoiceListSerializer


def test_question_and_choice_viewset_list(choice_and_question_list_expected_schema):
    result = ColumnProcessor(ChoiceListSerializer(), {}).get_schema()
    assert result == choice_and_question_list_expected_schema
