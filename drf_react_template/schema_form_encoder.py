import re
from typing import Any, Dict, List, Optional, Tuple, Union

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import fields, serializers

SerializerType = Union[
    serializers.BaseSerializer,
    serializers.Serializer,
    serializers.ListSerializer,
    serializers.Field,
]


class ProcessingMixin:
    TYPE_MAP_OVERRIDES_KEY = 'type_map_overrides'
    TYPE_MAP: Dict[str, Dict[str, str]] = {
        'CharField': {'type': 'string'},
        'IntegerField': {'type': 'integer', 'widget': 'updown'},
        'FloatField': {'type': 'number', 'widget': 'updown'},
        'DecimalField': {'type': 'number', 'widget': 'updown'},
        'BooleanField': {'type': 'boolean'},
        'DateTimeField': {'type': 'string', 'widget': 'date-time'},
        'DateField': {'type': 'string', 'widget': 'date'},
        'URLField': {'type': 'string', 'widget': 'uri'},
        'ChoiceField': {'type': 'string', 'enum': 'choices'},
        'EmailField': {'type': 'string', 'widget': 'email'},
        'ListField': {'type': 'array'},
    }

    def __init__(
        self,
        serializer: SerializerType,
        renderer_context: Dict[str, Any],
        prefix: str = '',
    ):
        self.serializer = serializer
        if self._is_list_serializer(serializer):
            self.fields = self._filter_fields(serializer.child.get_fields().items())
        else:
            self.fields = self._filter_fields(serializer.get_fields().items())
        self.renderer_context = renderer_context
        self.prefix = prefix
        self.type_map_overrides: Dict[str, Dict[str, str]] = self.renderer_context.get(
            self.TYPE_MAP_OVERRIDES_KEY, {}
        )

    def _get_type_map_value(self, field: SerializerType, name: Optional[str] = None):
        result = None
        if name:
            result = self.type_map_overrides.get(name)
        if not result:
            result = self.TYPE_MAP.get(type(field).__name__, {})
        return result

    def _generate_data_index(self, name: str) -> str:
        return f'{self.prefix}.{name}' if self.prefix else name

    def _get_title(self, field: SerializerType, name: str) -> str:
        result = field.label
        if result is None:
            result = name.title().replace('_', ' ').replace('.', ': ')
        return result

    @staticmethod
    def _filter_fields(all_fields: Tuple) -> Tuple:
        return tuple((name, field) for name, field in all_fields if not field.read_only)

    @staticmethod
    def _is_field_serializer(obj: Any) -> bool:
        return isinstance(obj, serializers.BaseSerializer)

    @staticmethod
    def _is_list_serializer(obj: Any) -> bool:
        return isinstance(obj, serializers.ListSerializer)

    def _is_hidden_serializer(self) -> bool:
        return all(
            [
                self._get_type_map_value(field, self._generate_data_index(name)).get(
                    'widget'
                )
                == 'hidden'
                for name, field in self.fields
            ]
        )


class SchemaProcessor(ProcessingMixin):
    def _is_serializer_optional(self) -> bool:
        return (
            self.serializer.allow_empty
            or (not self.serializer.required)
            or self.serializer.allow_null
        )

    def _get_serializer_title(self) -> str:
        label = self.serializer.label
        if label is not None:
            return label
        if self._is_hidden_serializer():
            return ''
        if self._is_list_serializer(self.serializer):
            class_name = type(self.serializer.child).__name__
        else:
            class_name = type(self.serializer).__name__
        class_name = class_name.replace('Serializer', '')
        class_name = ' '.join(re.findall('[A-Z][^A-Z]*', class_name))
        return class_name

    def _required_fields(self) -> List[str]:
        return [
            name
            for name, field in self.fields
            if field.required and not self._is_field_serializer(field)
        ]

    def _get_field_properties(self, field: SerializerType, name: str) -> Dict[str, Any]:
        result = {}
        data_index = self._generate_data_index(name)
        type_map_obj = self._get_type_map_value(field, data_index)
        result['type'] = type_map_obj['type']
        result['title'] = self._get_title(field, name)
        if isinstance(field, serializers.ListField):
            if field.min_length:
                result['minItems'] = field.min_length
            result['items'] = self._get_field_properties(field.child, "")
            result['uniqueItems'] = True
        else:
            if field.allow_null:
                result['type'] = [result['type'], 'null']
            enum = type_map_obj.get('enum')
            if enum:
                if enum == 'choices':
                    choices = field.choices
                    result['enum'] = list(choices.keys())
                    result['enumNames'] = [v for v in choices.values()]
                if isinstance(enum, (list, tuple)):
                    if isinstance(enum, (list, tuple)):
                        result['enum'] = [item[0] for item in enum]
                        result['enumNames'] = [item[1] for item in enum]
                    else:
                        result['enum'] = enum
                        result['enumNames'] = [item for item in enum]
            try:
                result['default'] = field.get_default()
            except fields.SkipField:
                pass
        return result

    def _get_all_field_properties(self) -> Dict[str, Any]:
        result = {}
        for name, field in self.fields:
            if self._is_field_serializer(field):
                result[name] = SchemaProcessor(
                    field, self.renderer_context, prefix=self._generate_data_index(name)
                ).get_schema()
            else:
                result[name] = self._get_field_properties(field, name)
        return result

    def get_schema(self) -> Dict[str, Any]:
        if self._is_list_serializer(self.serializer):
            return {
                'title': self._get_serializer_title(),
                'type': 'array',
                'minItems': 0 if self._is_serializer_optional() else 1,
                'items': {
                    'type': 'object',
                    'required': self._required_fields(),
                    'properties': self._get_all_field_properties(),
                },
            }
        else:
            return {
                'title': self._get_serializer_title(),
                'type': 'object',
                'required': self._required_fields(),
                'properties': self._get_all_field_properties(),
            }


class UiSchemaProcessor(ProcessingMixin):
    def _field_order(self) -> List[str]:
        return self.serializer.Meta.fields

    def _get_ui_field_properties(
        self, field: SerializerType, name: str
    ) -> Dict[str, Any]:
        data_index = self._generate_data_index(name)
        result = {}
        if self._is_field_serializer(field):
            return UiSchemaProcessor(
                field, self.renderer_context, prefix=data_index
            ).get_ui_schema()
        elif isinstance(field, serializers.ListField):
            child = field.child
            widget = self._get_type_map_value(field=child, name=data_index).get(
                'widget'
            )
            if not widget and isinstance(child, serializers.ChoiceField):
                widget = 'checkbox'
        else:
            widget = self._get_type_map_value(field=field, name=data_index).get(
                'widget'
            )
        help_text = field.help_text
        if widget:
            result['ui:widget'] = widget
        if help_text:
            result['ui:help'] = help_text
        result.update(field.style or {})
        return result

    def _get_all_ui_properties(self) -> Dict[str, Any]:
        result = {}
        for name, field in self.fields:
            result[name] = self._get_ui_field_properties(field, name)
        return result

    def get_ui_schema(self) -> Dict[str, Any]:
        if self._is_list_serializer(self.serializer):
            return {
                'items': {
                    **{'ui:order': self._field_order()},
                    **self._get_all_ui_properties(),
                }
            }
        else:
            return {
                **{'ui:order': self._field_order()},
                **self._get_all_ui_properties(),
            }


class ColumnProcessor(ProcessingMixin):
    LIST_FIELDS_KEY: str = 'list_fields'
    LIST_FIELDS_SORT_KEY: str = 'list_fields_sort'

    def __init__(
        self,
        serializer: SerializerType,
        renderer_context: Dict[str, Any],
        prefix: str = '',
    ):
        super(ColumnProcessor, self).__init__(serializer, renderer_context, prefix)
        self.list_fields: List[str] = self.renderer_context.get(
            self.LIST_FIELDS_KEY, []
        )
        self.list_sort: Dict[str, str] = self.renderer_context.get(
            self.LIST_FIELDS_SORT_KEY, {}
        )
        self._validate_list_params()

    def _validate_list_params(self):
        if self.list_fields:
            if any(not isinstance(name, str) for name in self.list_fields):
                raise TypeError('The list_fields must be a list of strings, or empty')
        if self.list_sort:
            if self.list_fields and any(
                name not in self.list_fields for name in self.list_sort.keys()
            ):
                raise KeyError(
                    'The list_sort must be a dict where all the keys '
                    'are in list_fields (if it is used)'
                )
            if any(val not in ['ascend', 'descend'] for val in self.list_sort.values()):
                raise ValueError(
                    'Every value in list_sort should be either "ascend" or "descend"'
                )

    def _get_column_properties(
        self, field: SerializerType, name: str
    ) -> Dict[str, str]:
        data_index = self._generate_data_index(name)
        result = {
            'title': self._get_title(field, data_index),
            'dataIndex': data_index,
            'key': name,
        }
        sort_order = self.list_sort.get(data_index)
        if sort_order:
            result['defaultSortOrder'] = sort_order
        return result

    def get_schema(self) -> List[Dict[str, str]]:
        result = []
        for name, field in self.fields:
            data_index = self._generate_data_index(name)
            if self._is_field_serializer(field):
                # TODO: How to list nested list serializers?
                if self._is_list_serializer(field):
                    continue
                result.extend(
                    ColumnProcessor(
                        field, self.renderer_context, prefix=data_index
                    ).get_schema()
                )
            else:
                if self.list_fields and data_index not in self.list_fields:
                    continue
                result.append(self._get_column_properties(field, name))
        return result


class SerializerEncoder(DjangoJSONEncoder):
    LIST_ACTION = 'list'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            skipkeys=kwargs.pop('skipkeys', False),
            ensure_ascii=kwargs.pop('ensure_ascii', True),
            check_circular=kwargs.pop('check_circular', True),
            allow_nan=kwargs.pop('allow_nan', True),
            indent=kwargs.pop('indent', None),
            separators=kwargs.pop('separators', None),
            default=kwargs.pop('default', None),
            sort_keys=kwargs.pop('sort_keys', False),
        )
        self.renderer_context = kwargs.pop('renderer_context', {})
        self.extra_kwargs = kwargs

    def _get_view_action(self) -> str:
        return self.renderer_context.get('view', {}).__dict__.get('action', '')

    def default(self, obj: Any) -> Union[Dict, List]:
        if isinstance(obj, serializers.Serializer):
            if self._get_view_action() == self.LIST_ACTION:
                return ColumnProcessor(obj, self.renderer_context).get_schema()
            else:
                return {
                    'schema': SchemaProcessor(obj, self.renderer_context).get_schema(),
                    'uiSchema': UiSchemaProcessor(
                        obj, self.renderer_context
                    ).get_ui_schema(),
                }
        return super().default(obj)
