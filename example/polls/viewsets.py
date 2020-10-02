from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from drf_react_template.mixins import FormSchemaViewSetMixin
from example.polls import models, serializers


class PollViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    FormSchemaViewSetMixin,
):
    queryset = models.Question.objects.all().prefetch_related('choice_set')

    type_map_overrides = {
        'pub_date': {'type': 'string', 'widget': 'DatePickerWidget'},
        'question_text': {'type': 'string', 'widget': 'textarea'},
        'choices.choice_text': {'type': 'string', 'widget': 'textarea'},
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.QuestionListSerializer
        return serializers.ChoiceSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            id=self.kwargs['pk'],
        )
