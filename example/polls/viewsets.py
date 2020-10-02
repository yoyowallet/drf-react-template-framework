from django.shortcuts import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from drf_react_template.mixins import FormSchemaViewSetMixin
from example.polls import models, serializers


class PollViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    FormSchemaViewSetMixin,
):
    queryset = models.Choice.objects.all().prefetch_related('questions')

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
        return get_object_or_404(
            self.get_queryset(),
            id=self.kwargs['pk'],
        )
