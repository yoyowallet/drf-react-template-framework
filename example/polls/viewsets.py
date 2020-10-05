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
    serializer_class = serializers.QuestionSerializer
    serializer_list_class = serializers.QuestionListSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            id=self.kwargs['pk'],
        )
