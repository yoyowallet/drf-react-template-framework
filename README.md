# Django Rest Framework React Template Framework
Django Rest Framework React Template Framework is a Python package that plugs into [Django Rest Framework](https://www.django-rest-framework.org/) to generate json schemas for [react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form). The concept is similar to the DRF [HTMLFormRenderer](https://www.django-rest-framework.org/api-guide/renderers/#htmlformrenderer), but specifically designed for [React](https://reactjs.org/) frontends.

## Installation

TODO

## Quick Start

See `/example` for a complete simple example.


`serializers.py`:
```python
from rest_framework import serializers

class ChoiceSerializer(serializers.ModelSerializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField()

    class Meta:
        fields = ('choice_text', 'votes')
```
`viewsets.py`:
```python
from rest_framework.mixins import RetrieveModelMixin
from drf_react_template.mixins import FormSchemaViewSetMixin
from example.polls import models, serializers

class ChoiceViewSet(
    RetrieveModelMixin,
    FormSchemaViewSetMixin,
):
    queryset = models.Choice.objects.all()
    serializer_class = serializers.ChoiceSerializer
```
Now when the retrieve endpoint is called, `FormSchemaViewSetMixin` will update the response
to include a `serializer` object in the json, while the original payload is sorted in `formData`.

Inside the `serializer` object, two fields `schema` and `uiSchema` contain the objects which
can be used inside [`react-jsonschema-form`](https://react-jsonschema-form.readthedocs.io/en/latest/#usage).

## Documentation
