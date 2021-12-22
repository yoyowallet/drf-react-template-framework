import re
from typing import Any, Dict, List, Tuple, Union

from django.conf import settings
from django.core import validators
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import fields, serializers
from rest_framework import validators as drf_validators

SerializerType = Union[
    serializers.BaseSerializer,
    serializers.Serializer,
    serializers.ListSerializer,
    serializers.Field,
]

SCHEMA_OVERRIDE_KEY = 'schema:override'
UI_SCHEMA_OVERRIDE_KEY = 'uiSchema:override'
COLUMN_PROCESSOR_OVERRIDE_KEY = 'column:override'
OVERRIDE_KEYS = {
    SCHEMA_OVERRIDE_KEY,
    UI_SCHEMA_OVERRIDE_KEY,
    COLUMN_PROCESSOR_OVERRIDE_KEY,
}

DEPENDENCY_SIMPLE_KEY = 'schema:dependencies:simple'
DEPENDENCY_CONDITIONAL_KEY = 'schema:dependencies:conditional'
DEPENDENCY_DYNAMIC_KEY = 'schema:dependencies:dynamic'
DEPENDENCY_OVERRIDE_KEY = 'schema:dependencies:override'
DEPENDENCY_KEYS = {
    DEPENDENCY_SIMPLE_KEY,
    DEPENDENCY_CONDITIONAL_KEY,
    DEPENDENCY_DYNAMIC_KEY,
    DEPENDENCY_OVERRIDE_KEY,
}

STYLE_KEYS_TO_IGNORE = {
    *OVERRIDE_KEYS,
    *DEPENDENCY_KEYS,
}

VALIDATION_MAP = {
    validators.MaxLengthValidator: ['maxLength', lambda v: v.limit_value],
    validators.MinLengthValidator: ['minLength', lambda v: v.limit_value],
    validators.MaxValueValidator: ['maximum', lambda v: v.limit_value],
    validators.MinValueValidator: ['minimum', lambda v: v.limit_value],
    validators.RegexValidator: ['pattern', lambda v: v.regex.pattern],
}

EXCLUDED_VALIDATOR_CLASSES = [
    validators.ProhibitNullCharactersValidator,
    drf_validators.ProhibitSurrogateCharactersValidator,
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
        'RegexField': {'type': 'string', 'widget': 'regex'},
        'ImageField': {'type': 'file', 'widget': 'file'},
        'ListField': {'type': 'array'},
    }

    def __init__(
        self,
        serializer: SerializerType,
        renderer_context: Dict[str, Any],
        prefix: str = '',
        extra_types: Dict[str, Any] = {},
    ):
        self.serializer = serializer
        if self._is_list_serializer(serializer):
            self.fields = self._filter_fields(serializer.child.fields.items())
        else:
            self.fields = self._filter_fields(serializer.fields.items())
        self.renderer_context = renderer_context
        self.prefix = prefix
        self.extra_types = extra_types
        self.extra_types.update(getattr(settings, 'DRF_REACT_TEMPLATE_TYPE_MAP', {}))
        self.TYPE_MAP.update(self.extra_types)

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
    def __init__(
        self,
        serializer: SerializerType,
        renderer_context: Dict[str, Any],
        prefix: str = '',
        extra_types: Dict[str, Any] = {},
    ):
        super().__init__(serializer, renderer_context, prefix, extra_types)
        self.fields_to_be_removed = set()
        self.fields_to_be_kept = set()

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

    def _set_validation_properties(
        self, field: SerializerType, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        for validator in field.validators:
            for validator_class, attr_value in VALIDATION_MAP.items():
                if isinstance(validator, validator_class):
                    result_key, result_filter = attr_value
                    result[result_key] = result_filter(validator)

        return result

    def _get_field_properties(self, field: SerializerType, name: str) -> Dict[str, Any]:
        result = {}
        type_map_obj = self._get_type_map_value(field)
        result['type'] = type_map_obj['type']
        result['title'] = self._get_title(field, name)
        if isinstance(field, serializers.ListField):
            if field.allow_empty:
                result['required'] = not getattr(field, 'allow_empty', True)
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

        result = self._set_validation_properties(field, result)

        return result

    def _get_all_field_properties(self) -> Dict[str, Any]:
        result = {}
        for name, field in self.fields:
            if self._is_field_serializer(field):
                result[name] = SchemaProcessor(
                    field, self.renderer_context, prefix=self._generate_data_index(name)
                ).get_schema()
            else:
                override = field.style.get(SCHEMA_OVERRIDE_KEY)
                result[name] = override or self._get_field_properties(field, name)
        return result

    def _remove_from_required(
        self, schema: Dict[str, Any], field_name: str
    ) -> Dict[str, Any]:
        try:
            if self._is_list_serializer(self.serializer):
                schema['items']['required'].remove(field_name)
            else:
                schema['required'].remove(field_name)
        except ValueError:
            pass
        return schema

    def _get_from_properties(
        self, schema: Dict[str, Any], field_name: str, pop: bool = False
    ) -> Dict[str, Any]:
        if self._is_list_serializer(self.serializer):
            properties = (
                schema['items']['properties'].pop(field_name)
                if pop
                else schema['items']['properties'].get(field_name)
            )
        else:
            properties = (
                schema['properties'].pop(field_name)
                if pop
                else schema['properties'].get(field_name)
            )
        return properties

    def _simple_dependency(
        self, dependent_properties: Union[str, List[str]], schema: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Any]]:
        if not isinstance(dependent_properties, list):
            dependent_properties = [dependent_properties]
        for field_name in dependent_properties:
            schema = self._remove_from_required(schema, field_name)
            self.fields_to_be_kept.add(field_name)
        return dependent_properties, schema

    def _conditional_dependency(
        self, dependent_properties: Union[str, List[str]], schema: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if not isinstance(dependent_properties, list):
            dependent_properties = [dependent_properties]
        dependency_object = {'properties': {}, 'required': []}
        for field_name in dependent_properties:
            self.fields_to_be_removed.add(field_name)
            schema = self._remove_from_required(schema, field_name)
            properties = self._get_from_properties(schema, field_name, pop=False)
            dependency_object['properties'][field_name] = properties
            dependency_object['required'].append(field_name)
        return dependency_object, schema

    @staticmethod
    def _create_enum_dependency_object(
        field_name: str, enum_key: str, main_properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        if enum_key not in main_properties['enum']:
            raise KeyError(
                f"'{enum_key}' is not a valid enum, the options are: "
                f"{main_properties['enum']}"
            )
        idx = main_properties['enum'].index(enum_key)
        enum_dependency_object = {
            'properties': {field_name: main_properties.copy()},
            'required': [],
        }
        enum_dependency_object['properties'][field_name]['enum'] = [enum_key]
        enum_dependency_object['properties'][field_name]['enumNames'] = [
            main_properties['enumNames'][idx]
        ]

        return enum_dependency_object

    def _dynamic_dependency(
        self, name: str, dependent_properties: Dict[str, Any], schema: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        main_properties = self._get_from_properties(schema, name, pop=False)
        if 'enum' not in main_properties:
            raise KeyError('Only enumerable fields can have dynamic dependencies')
        dependency_object = {'oneOf': []}
        for enum_key, dep_fields in dependent_properties.items():
            enum_dependency_object = self._create_enum_dependency_object(
                name, enum_key, main_properties
            )
            if not dep_fields:
                dep_fields = []
            elif not isinstance(dep_fields, list):
                dep_fields = [dep_fields]
            for field_name in dep_fields:
                self.fields_to_be_removed.add(field_name)
                schema = self._remove_from_required(schema, field_name)
                properties = self._get_from_properties(schema, field_name, pop=False)
                enum_dependency_object['properties'][field_name] = properties
                enum_dependency_object['required'].append(field_name)
            dependency_object['oneOf'].append(enum_dependency_object)
        return dependency_object, schema

    def _add_dependencies(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        dependencies = {}
        for name, field in self.fields:
            dependency_object = {}
            style_keys = set(field.style.keys())
            dep_key = list(DEPENDENCY_KEYS.intersection(style_keys))
            if dep_key:
                if len(dep_key) > 1:
                    raise KeyError(
                        f"Cannot have multiple types of dependencies on a field."
                        f"Please select one of: '{DEPENDENCY_SIMPLE_KEY}', "
                        f"'{DEPENDENCY_CONDITIONAL_KEY}', '{DEPENDENCY_OVERRIDE_KEY}'"
                    )
                dep_key = dep_key[0]
            else:
                continue
            dependent_properties = field.style[dep_key]

            if dep_key == DEPENDENCY_SIMPLE_KEY:
                dependency_object, schema = self._simple_dependency(
                    dependent_properties, schema
                )
            elif dep_key == DEPENDENCY_CONDITIONAL_KEY:
                dependency_object, schema = self._conditional_dependency(
                    dependent_properties, schema
                )
            elif dep_key == DEPENDENCY_DYNAMIC_KEY:
                dependency_object, schema = self._dynamic_dependency(
                    name, dependent_properties, schema
                )
            elif dep_key == DEPENDENCY_OVERRIDE_KEY:
                dependency_object = dependent_properties
            dependencies[name] = dependency_object

        for field_name in self.fields_to_be_removed.difference(self.fields_to_be_kept):
            self._get_from_properties(schema, field_name, pop=True)  # In place mutation
        if dependencies:
            schema['dependencies'] = dependencies
        return schema

    def get_schema(self) -> Dict[str, Any]:
        if self._is_list_serializer(self.serializer):
            schema = {
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
            schema = {
                'title': self._get_serializer_title(),
                'type': 'object',
                'required': self._required_fields(),
                'properties': self._get_all_field_properties(),
            }
        schema = self._add_dependencies(schema)
        return schema


class UiSchemaProcessor(ProcessingMixin):
    def _field_order(self) -> List[str]:
        if self._is_list_serializer(self.serializer):
            return list(self.serializer.child.Meta.fields)
        return list(self.serializer.Meta.fields)

    def _get_style_dict(self, field) -> Dict[str, Any]:
        style_dict = {}
        for k, v in field.style.items():
            if not k.startswith("schema:") and k not in STYLE_KEYS_TO_IGNORE:
                style_dict[k] = v
        return style_dict

    def _set_validation_properties(
        self, field: SerializerType, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        excluded_validators = tuple(
            EXCLUDED_VALIDATOR_CLASSES + list(VALIDATION_MAP.keys())
        )
        custom_validators = [
            v for v in field.validators if not isinstance(v, excluded_validators)
        ]
        if custom_validators:
            result['ui:custom-validators'] = [
                {
                    'code': getattr(v, 'code', v.__class__.__name__.lower()),
                    'message': getattr(v, 'message'),
                }
                for v in custom_validators
            ]

        return result

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
        result.update(self._get_style_dict(field))
        result = self._set_validation_properties(field, result)
        return result

    def _get_all_ui_properties(self) -> Dict[str, Any]:
        result = {}
        for name, field in self.fields:
            override = field.style.get(UI_SCHEMA_OVERRIDE_KEY)
            result[name] = override or self._get_ui_field_properties(field, name)
        return result

    def get_ui_schema(self) -> Dict[str, Any]:
        if self._is_list_serializer(self.serializer):
            return {
                'items': {
                    **{'ui:order': self._field_order()},
                    **self._get_style_dict(self.serializer),
                    **self._get_all_ui_properties(),
                }
            }
        else:
            return {
                **{'ui:order': self._field_order()},
                **self._get_style_dict(self.serializer),
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
                override = field.style.get(COLUMN_PROCESSOR_OVERRIDE_KEY)
                result.append(override or self._get_column_properties(field, name))
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
