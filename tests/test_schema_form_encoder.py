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


@pytest.mark.parametrize(
    ['class_name', 'form_name'],
    (
        ['TitleSerializer', 'Title'],
        ['Title', 'Title'],
        ['TitleAndSubtitle', 'Title And Subtitle'],
    ),
)
def test_serializer_title(class_name, form_name):
    ChoiceSerializer.__name__ = class_name

    result = SchemaProcessor(ChoiceSerializer(), {}).get_schema()
    assert result['title'] == form_name


def test_serializer_no_title():
    class NoTitleSerializer(ChoiceSerializer):
        def __init__(self, **kwargs):
            super().__init__(label='', **kwargs)

    result = SchemaProcessor(NoTitleSerializer(), {}).get_schema()
    assert result['title'] == ''


def test_field_label():
    new_label = 'test_label'

    class LabelSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(label=new_label)

    result = SchemaProcessor(LabelSerializer(), {}).get_schema()
    assert result['properties']['choice_text']['title'] == new_label

    result = ColumnProcessor(LabelSerializer(), {}).get_schema()
    assert result[0]['title'] == new_label


def test_field_hidden_label():
    new_label = 'test_label'
    style_dict = {'ui:options': {'label': False}}

    class LabelSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(label=new_label, style=style_dict)

    result = SchemaProcessor(LabelSerializer(), {}).get_schema()
    assert result['properties']['choice_text']['title'] == new_label

    result = UiSchemaProcessor(LabelSerializer(), {}).get_ui_schema()
    assert result['choice_text'] == style_dict


def test_read_only():
    class ReadOnlySerializer(ChoiceSerializer):
        choice_text = serializers.CharField(read_only=True)

    result = SchemaProcessor(ReadOnlySerializer(), {}).get_schema()
    assert 'choice_text' not in result['properties']

    result = UiSchemaProcessor(ReadOnlySerializer(), {}).get_ui_schema()
    assert 'choice_text' not in result

    result = ColumnProcessor(ReadOnlySerializer(), {}).get_schema()
    assert not any(d['key'] == 'choice_text' for d in result)


def test_required():
    class RequiredSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(required=False)

    result = SchemaProcessor(RequiredSerializer(), {}).get_schema()
    assert 'choice_text' not in result['required']


def test_allow_null():
    class AllowNullSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(allow_null=True)

    result = SchemaProcessor(AllowNullSerializer(), {}).get_schema()
    assert len(result['properties']['choice_text']['type']) == 2
    assert 'null' in result['properties']['choice_text']['type']


def test_default():
    new_default = 'default'

    class DefaultSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(default=new_default)

    result = SchemaProcessor(DefaultSerializer(), {}).get_schema()
    assert result['properties']['choice_text']['default'] == new_default
    assert 'choice_text' not in result['required']


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


def test_choice_placeholder():
    new_placeholder = 'new_placeholder'

    class PlaceholderSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(style={'ui:placeholder': new_placeholder})

    result = UiSchemaProcessor(PlaceholderSerializer(), {}).get_ui_schema()
    assert result['choice_text']['ui:placeholder'] == new_placeholder


def test_choice_text_area_rows():
    widget = 'textarea'
    ui_options = {'rows': 8}

    class TextAreaWidgetSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(
            style={
                'ui:widget': widget,
                'ui:options': ui_options,
            }
        )

    result = UiSchemaProcessor(TextAreaWidgetSerializer(), {}).get_ui_schema()
    assert result['choice_text']['ui:widget'] == widget
    assert result['choice_text']['ui:options'] == ui_options


def test_choice_disabled():
    class DisabledSerializer(ChoiceSerializer):
        choice_text = serializers.CharField(style={'ui:disabled': 'true'})

    result = UiSchemaProcessor(DisabledSerializer(), {}).get_ui_schema()
    assert result['choice_text']['ui:disabled'] == 'true'


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
