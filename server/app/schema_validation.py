from collections import defaultdict
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, create_model, Field
from pydantic.json_schema import JsonSchemaValue
from functools import reduce


def validate_with_model_schema(schema: JsonSchemaValue, values: dict, stric: bool = False) -> BaseModel:
    """Validate values with the schema from the model

    Parameters:
    -----------
    schema : JsonSchemaValue
        JSON schema of the model. From `pydantic.BaseModel.model_json_schema()`
    values : dict
        Values to validate

    Returns:
    --------
    dict
        Validated values

    Raises:
    -------
    ValueError
        If the values are invalid
    """
    model = create_model_from_schema(schema)
    return model.model_validate(values, strict=stric)


def create_model_from_schema(schema: dict, type_mapper: dict | None = None) -> type[BaseModel]:
    """Create a Pydantic model from a JSON schema"""
    if type_mapper is None:
        type_mapper = {
            "any": Any,
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "object": dict,
            "array": list,
            "null": None,
        }
        type_mapper.update(_define_enum_types(schema))
        for submodel in _get_sorted_submodels(schema):
            type_mapper.update(_define_submodel_types(schema, submodel, type_mapper))

    model = create_model(
        schema["title"],
        __doc__=schema.get("description", ""),
        **_parse_fields(schema, type_mapper)
    ) #  type: ignore
    return model


def _define_enum_types(schema: dict) -> dict[str, type]:
    defs = schema.get("$defs", {})
    types = {}
    for name, definition in defs.items():
        if 'enum' not in definition:
            continue
        enum_type = Enum(name, {f'value_{idx}': value for idx, value in enumerate(definition['enum'])})
        enum_type.__doc__ = definition.get('description', '')
        types[f'#/$defs/{name}'] = enum_type
    return types


def _define_submodel_types(schema: dict, submodel: str, type_mapper: dict) -> dict[str, type]:
    defs = schema.get("$defs", {})
    types = {}
    # for name, definition in defs.items():
    #     if 'properties' not in definition:
    #         continue
    definition = defs[submodel]
    types[f'#/$defs/{submodel}'] = create_model_from_schema(definition, {**type_mapper, **types})
    return types

def _resolve_type(metadata: dict, type_mapper: dict) -> type:
    if "$ref" in metadata:
        field_type = type_mapper.get(metadata["$ref"], Any)
    elif "anyOf" in metadata:
        field_type: type = reduce(lambda a, b: a | b, (_resolve_type(sub_metadata, type_mapper) for sub_metadata in metadata["anyOf"]))  # type: ignore
    else:
        field_type = type_mapper[metadata.get("type", "any")]
    if field_type is dict and 'additionalProperties' in metadata:
        sub_field_type = _resolve_type(metadata['additionalProperties'], type_mapper)
        field_type = dict[Any, sub_field_type]
    elif field_type is list and 'items' in metadata:
        sub_field_type = _resolve_type(metadata['items'], type_mapper)
        field_type = list[sub_field_type]
    return field_type


def _parse_fields(schema: dict, type_mapper: dict) -> dict[str, Annotated]:
    properties = schema.get("properties", {})
    fields = {}
    for field, metadata in properties.items():
        field_type = _resolve_type(metadata, type_mapper)
        fields[field] = Annotated[field_type, Field(description=metadata.get("description"), default=metadata.get("default", ...))]
    return fields

def _get_sorted_submodels(schema: dict) -> list[str]:
    defs = schema.get("$defs", {})
    depends: dict[str, list[str]] = defaultdict(list)
    enabler: dict[str, list[str]] = defaultdict(list)
    submodels_names = [ name for name in defs.keys() if 'properties' in defs[name] ]
    for name in submodels_names:
        definition = defs[name]
        for prop in definition['properties'].values():
            if "$ref" not in prop or prop["$ref"].split('/')[-1] not in submodels_names:
                continue
            depend_name = prop["$ref"].split('/')[-1]
            enabler[depend_name].append(name)
            depends[name].append(depend_name)
    submodels = []
    curr_model = submodels_names.pop()
    seen = set()
    while len(submodels_names) >= 0:
        if depends[curr_model]:
            submodels_names.append(curr_model)
            seen.add(curr_model)
            curr_model = depends[curr_model][0]
            submodels_names.remove(curr_model)
            if curr_model in seen:
                ValueError("Circular dependency")
        else:
            seen = set()
            submodels.append(curr_model)
            for model in enabler[curr_model]:
                depends[model].remove(curr_model)

            if enabler[curr_model]:
                curr_model = enabler[curr_model].pop()
                submodels_names.remove(curr_model)
            elif submodels_names:
                curr_model = submodels_names.pop()
            else:
                break
    return submodels
