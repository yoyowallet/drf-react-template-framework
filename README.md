# Django Rest Framework React Template Framework
Django Rest Framework React Template Framework is a Python package that plugs into [Django Rest Framework](https://www.django-rest-framework.org/) to generate json schemas for [react-jsonschema-form](https://github.com/rjsf-team/react-jsonschema-form). The concept is similar to the DRF [HTMLFormRenderer](https://www.django-rest-framework.org/api-guide/renderers/#htmlformrenderer), but specifically designed for [React](https://reactjs.org/) frontends.

## Installation
```
pip install drf-react-template-framework
```

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

At the class level the serializer defines the form name:
```
ChoiceSerializer -> Choice
QuestionAndChoiceSerializer -> Question And Choice
Choice -> Choice
```
If a different title is required (or no title for nested forms), then the `__init__` method can be updated:
```python
def __init__(self, *args, **kwargs):
    kwargs['label'] = 'New Form Title'
    super().__init__(*args, **kwargs)
```

#### Serializer Field Attributes

The following is a list of parameters that can be added to individual fields which modifies 
`react-jsonschema-form` functionality on the front-end.

##### Label
Updates the form input title text. Can also be used to provide translations.
```python
choice_text = serializers.CharField(label='What is the choice label?')
```
The label can also be disabled completely via `style`:
```python
choice_text = serializers.CharField(style={'ui:options': {'label': False}})
```
Note: This does not work for `list` actions.

##### Read Only
Setting `read_only=True` forces the encoder to skip it when building the form, 
but still means the value gets sent in the `formData`:
```python
choice_text = serializers.CharField(read_only=True)
```
This is useful for custom widgets which rely on data not related to the form (e.g. `id`).

##### Required
Setting `required=False` removes frontend validation of the field:
```python
choice_text = serializers.CharField(required=False)
```
Note: This has no effect on `list` actions.

##### Allow Null
Setting `allow_null=True` allows `null` values to be sent back in `formData`:
```python
choice_text = serializers.CharField(allow_null=True)
```
Note: This has no effect on `list` actions.

##### Default
By setting a default value, a field is automatically set to `required=False`. 
The `formData` object will also contain the `default` value if it is not provided one.
```python
choice_text = serializers.CharField(default='example text')
```
Note: This has no effect on `list` actions.

##### Style
The DRF `style` parameter is a `dict` and is therefore used for a number of different parameters. 
There are a [number of options](https://react-jsonschema-form.readthedocs.io/en/latest/api-reference/uiSchema/) 
that `react-jsonschema-form` provides, many of which should work out-of-the-box, 
although not all options will have been tested.

Since style params are applied **last**, they can overwrite other keys. Additionally, any key not
starting with `schema:` will be sent in the `json` payload, so this can be a good place to send
additional attributes for custom widgets.

The following are a list of valid (tested) keys and their uses.

**Note**: This can also be done at the serializer level:
```python
def __init__(self, *args, **kwargs):
    kwargs['style'] = {'ui:template': 'Card'}
    super().__init__(*args, **kwargs)
```

###### Dependencies

`react-jsonschema-form` allows for the use of [dependencies](https://react-jsonschema-form.readthedocs.io/en/latest/usage/dependencies/#dependencies) 
between multiple fields. This library has analogues for the four types (bidirectional, unidirectional, conditional, and
dynamic).
```python
# Unidirectional
choice_text = serializers.CharField(
    style={'schema:dependencies:simple': ['votes']}
)

# Bidirectional - note the different value styles, either is fine.
choice_text = serializers.CharField(
    style={'schema:dependencies:simple': ['votes']}
)
votes = serializers.IntegerField(
    default=0, style={'schema:dependencies:simple': 'choice_text'}
)

# Conditional
choice_text = serializers.CharField(
    style={'schema:dependencies:conditional': ['votes']}
)

# Dynamic - must be an enum field, and only one choice per dependency,
# multiple choices can have the same dependencies (side-stepping this issue).
choice_text = serializers.ChoiceField(
    choices=(('yes', 'Yes'), ('no', 'No')),
    style={'schema:dependencies:dynamic': {'yes': ['votes'], 'no': None}}
)
```

###### Field Overrides 

Since this framework doesn't cover 100% of the features of the `react-jsonschema-form`, it is possible to provide 
`dict` objects which override the individual field properties:
```python
choice_text = serializers.CharField(
    style={
        'schema:override': {'type': 'string', 'title': 'Overridden title'},
        'uiSchema:override': {'ui:widget': 'updown'},
        'column:override': {
            'title': 'Overridden title',
            'dataIndex': 'question_text',
            'key': 'question_text',
        },
        'schema:dependencies:override': ['votes']
    }
)
```
**Note**: There is no validation around these overrides, so it is left up to the developer to ensure the resulting
schema is valid. For example, `'schema:dependencies:override'` will not remove fields from the main `'properties'` or 
`'required'` objects. (This can be done by omitting the dependant field from the serializer or using `read_only=True`).

###### List Sort Order
Sends the `defaultSortOrder` key with the `list` action serializer:
```python
choice_text = serializers.CharField(, style={'schema:sort': 'ascend'})
```

###### Widget, Type, and Enum
While the framework tries to provide sensible defaults for DRF fields, 
sometimes custom frontend widgets need to provide custom behaviour. 
```python
choice_text = serializers.CharField(style={
    'ui:widget': 'textarea',
    'schema:type': 'string',
    'schema:enum': 'choices'
})
```
More information can be found on 
[`types`](https://react-jsonschema-form.readthedocs.io/en/latest/usage/single/#field-types)
and [`enum`](https://react-jsonschema-form.readthedocs.io/en/latest/usage/single/#enumerated-values).

`enum` can also be set to the `string` `choices` (as in the example), 
to try and use the `field.choices` attribute.

###### Placeholder
The HTML placeholder text can be updated in the following way:
```python
choice_text = serializers.CharField(style={'ui:placeholder': 'This a placeholder value'})
```

###### Text Area Widget Rows
When the `ui:widget` is set to `textarea` (see above), the `rows` can be set via:
```python
choice_text = serializers.CharField(style={
    'ui:widget': 'textarea',
    'ui:options': {'rows': 8},
})
``` 

###### Disabled
An input field can be `disabled` in the following way:
```python
choice_text = serializers.CharField(style={'ui:disabled': 'true'})
```
