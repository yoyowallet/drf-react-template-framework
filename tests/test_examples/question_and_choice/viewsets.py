from django_mock_queries.query import MockModel, MockSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from drf_react_template.mixins import FormSchemaViewSetMixin
from tests.test_examples.question_and_choice import serializers


class CustomerFeedbackViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    FormSchemaViewSetMixin,
):
    queryset = MockSet(
        MockModel(choice_text='Make a choice 1', votes=13),
        MockModel(choice_text='Make a choice 2', votes=14),
        MockModel(choice_text='Make a choice 3', votes=15),
    )

    type_map_overrides = {
        'questions.pub_date': {'type': 'string', 'widget': 'DatePickerWidget'},
        'questions.question_text': {'type': 'string', 'widget': 'textarea'},
        'choice_text': {'type': 'string', 'widget': 'textarea'},
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ChoiceListSerializer
        return serializers.ChoiceSerializer

    def get_object(self):
        return MockModel(choice_text='Make a choice', votes=10, questions=[])
