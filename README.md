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

While the above quick start is useful for super simple cases,
the framework has a large number of additional parameters which can be used to customize behaviour.

### Viewset

All viewsets must inherit from `drf_react_template.mixins.FormSchemaViewSetMixin`. 
This class inherits from the 
DRF [`GenericViewSet`](https://www.django-rest-framework.org/api-guide/viewsets/#genericviewset), 
while additionally providing custom `finialize response functionality` and the additional endpoint:
```
GET */create/
>> {'serializer': ..., 'formData': {}}
```
Which can be used to generate an empty form for create. 

The only other specific customization that can be applied in the viewset is different 
serializers for different endpoints. For example, `update` actions often show a subset of fields;
as such it is possible to override `get_serializer_class` to return the specific form required. 

For example:
```python
# serializers.py
class ChoiceSerializer(serializers.ModelSerializer):
    choice_text = serializers.CharField()
    votes = serializers.IntegerField()

    class Meta:
        fields = ('choice_text', 'votes')

class ChoiceUpdateSerializer(serializers.ModelSerializer):
    choice_text = serializers.CharField()

    class Meta:
        fields = ('choice_text',)

# viewsets.py
def get_serializer_class(self):
    if self.action == 'update':
        return ChoiceUpdateSerializer
    return ChoiceSerializer
```

Since this having a separate `list` serializer is so common, the above can be avoided by using
the `serializer_list_class` class attribute provided by `FormSchemaViewSetMixin`.

### Serializer

The majority of the customization will occur inside serializer classes; 
a real world example will often require custom `create`, `update`, `to_representation`, etc methods. 

The following is a list of parameters that can be added to individual fields which modifies 
`react-jsonschema-form` functionality on the front-end.

#### Label
Updates the form input title text. Can also be used to provide translations.
```python
choice_text = serializers.CharField(label='What is the choice label?')
```

#### Style
The DRF `style` parameter is a `dict` and is therefore used for a number of different parameters. 
There are a [number of options](https://react-jsonschema-form.readthedocs.io/en/latest/api-reference/uiSchema/) 
that `react-jsonschema-form` provides, many of which should work out-of-the-box, 
although not all options will have been tested.

Since style params are applied **last**, they can overwrite other keys. 

The following are a list of valid (tested) keys and their uses. 

##### Widget
While the framework tries to provide sensible defaults for DRF fields, 
sometimes custom frontend widgets need to provide custom behaviour. 
```python
choice_text = serializers.CharField(style={"ui:widget": "textarea"})
```