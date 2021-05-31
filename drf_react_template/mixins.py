from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import Response
from rest_framework.viewsets import GenericViewSet

from drf_react_template.renderers import JSONSerializerRenderer


class FormSchemaViewSetMixin(GenericViewSet):
    renderer_classes = (JSONSerializerRenderer,)
    serializer_list_class = None

    def get_serializer_class(self):
        if self.action == 'list' and self.serializer_list_class:
            return self.serializer_list_class
        return self.serializer_class

    def finalize_response(self, request, response, *args, **kwargs):
        response = super(FormSchemaViewSetMixin, self).finalize_response(
            request, response, args, kwargs
        )
        if response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            response.data = {
                'serializer': self.get_serializer(),
                'formData': response.data,
            }
        return response

    @action(detail=False, methods=('get',), url_path='create')
    def create_form(self, request, *args, **kwargs):
        return Response({})
