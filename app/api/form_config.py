from typing import List

from pyql import Object
from pyql.utils.str_converters import to_camel_case

from .fields import AnyValue

FormFieldConfig = Object('FormFieldConfig', {
    'id': str,
    'value': AnyValue,
    'readable': bool,
    'editable': bool,
    'required': bool,
})


@FormFieldConfig.field('id')
def resolve_formfieldconfig_id(cfg, info) -> str:
    # This needs to match the field name in javascript
    return to_camel_case(cfg.id)


FormConfig = Object('FormConfig', {
    'editable': bool,
    'fields': List[FormFieldConfig],
})
