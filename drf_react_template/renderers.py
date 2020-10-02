import json

from rest_framework.renderers import (
    INDENT_SEPARATORS,
    LONG_SEPARATORS,
    SHORT_SEPARATORS,
    JSONRenderer,
)

from drf_react_template.schema_form_encoder import SerializerEncoder


class JSONSerializerRenderer(JSONRenderer):
    encoder_class = SerializerEncoder

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
            Include renderer_context in JsonEncoder
        """
        if data is None:
            return bytes()

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS
        ret = json.dumps(
            data,
            cls=self.encoder_class,
            indent=indent,
            ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict,
            separators=separators,
            renderer_context=renderer_context,
        )
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return bytes(ret.encode('utf-8'))
