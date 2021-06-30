# -*- coding: utf-8 -*-
import inspect
from typing import Optional, Dict, Any, Callable

from onetask import entities


def build_lf(
        function: Callable,
        programming_language_version: Optional[str] = "3"
) -> entities.LabelingFunction:
    """
    Creates a labeling function from a Python function object. The docstring of the function object will be interpreted
    as the documentation for the labeling function. If none is provided, the labeling function will have no doc.

    :param function: Python function object.
    :param programming_language_version: Python version of the function object.
    :return: Labeling Function as a onetask entity.
    """

    body = entities.LFBody(
        source_code=inspect.getsource(function).replace("    ", "\t"),
        programming_language_version=programming_language_version,
    )

    definition = entities.LFDefinition(
        body_type=body.__class__.__name__,
        description=inspect.getdoc(function)
    )

    lf = entities.LabelingFunction(
        definition=definition,
        body=body
    )
    return lf


def build_lf_from_dict(lf_dict) -> entities.LabelingFunction:
    """
    Creates a labeling function from a dictionary. This is only needed to recreate the onetask labeling function entities
    from server side. Do not use this method to create new labeling functions in the SDK; instead, you can use
    `build_lf`.

    :param lf_dict: Dictionary containing all information to build a labeling function, i.e.:
      * internal_id
      * definition: {body_type, description}
      * body: {source_code, programming_language_version}
    :return: Labeling Function as a onetask entity.
    """

    definition = entities.LFDefinition(
        internal_id=lf_dict["internal_id"],
        body_type=lf_dict["definition"]["body_type"],
        description=lf_dict["definition"]["description"],
    )

    # if more body types are added, check the body_type of the definition for construction
    body = entities.LFBody(
        source_code=lf_dict["body"]["source_code"],
        programming_language_version=lf_dict["body"]["programming_language_version"]
    )

    lf = entities.LabelingFunction(
        definition=definition,
        body=body
    )

    return lf


def build_record_from_dict(record_dict: Dict[str, Any]) -> entities.Record:
    """
    Creates a record from a dictionary. This is only needed to recreate the onetask record entities from server side.
    Do not use this method to create new record in the SDK

    :param record_dict: Dictionary containing all information to build a record, i.e.:
      * custom_id
      * noisy_annotation_list
      * attributes
      * embeddings
    :return: Record as a onetask entity.
    """

    record = entities.Record(
        custom_id=record_dict["custom_id"],
        annotation_list=record_dict["annotation_list"],
        attributes=record_dict["attributes"],
        embeddings=record_dict["embeddings"]
    )

    return record
