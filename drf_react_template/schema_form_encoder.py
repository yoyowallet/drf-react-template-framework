import re
from typing import Any, Dict, List, Tuple, Union

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import fields, serializers

SerializerType = Union[
    serializers.BaseSerializer,
    serializers.Serializer,
    serializers.ListSerializer,
    serializers.Field,
]


class ProcessingMixin:
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

    def _get_type_map_value(self, field: SerializerType):
        result = {
            'type': field.style.get('schema:type'),
            'enum': field.style.get('schema:enum'),
            'widget': field.style.get('ui:widget'),
        }
        result_default = self.TYPE_MAP.get(type(field).__name__, {})
        for k, v in result_default.items():
            if not result[k]:
                result[k] = result_default[k]
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
                self._get_type_map_value(field).get('widget') == 'hidden'
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
        type_map_obj = self._get_type_map_value(field)
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
        if self._is_list_serializer(self.serializer):
            return list(self.serializer.child.Meta.fields)
        return list(self.serializer.Meta.fields)

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
            widget = self._get_type_map_value(field=child).get('widget')
            if not widget and isinstance(child, serializers.ChoiceField):
                widget = 'checkbox'
        else:
            widget = self._get_type_map_value(field=field).get('widget')
        help_text = field.help_text
        if widget:
            result['ui:widget'] = widget
        if help_text:
            result['ui:help'] = help_text
        style_dict = {
            k: v for k, v in (field.style or {}).items() if not k.startswith("schema:")
        }
        result.update(style_dict)
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
    def _get_column_properties(
        self, field: SerializerType, name: str
    ) -> Dict[str, str]:
        data_index = self._generate_data_index(name)
        result = {
            'title': self._get_title(field, data_index),
            'dataIndex': data_index,
            'key': name,
        }
        sort_order = field.style.get('schema:sort')
        if sort_order:
            if sort_order not in ['ascend', 'descend']:
                raise ValueError(
                    f"The {data_index} field 'style['schema:sort']' "
                    f"value must be either 'ascend' or 'descend'"
                )
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
