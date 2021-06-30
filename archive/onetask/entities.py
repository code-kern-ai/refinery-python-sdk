# -*- coding: utf-8 -*-
import re
from abc import ABC
from typing import Optional, List, Dict, Any, Generator, Tuple

import numpy as np

from onetask.utils import object_utils


class OneTaskBaseEntity(ABC):
    """
    Base Entity for onetask entities.
    """

    def __repr__(self) -> str:
        return object_utils.create_representational_string(self)

    def __str__(self) -> str:
        return object_utils.create_display_string(self)

    def __iter__(self) -> Generator[Any, Tuple[str, Any], None]:
        return object_utils.create_generator(self)

    def __getitem__(self, item) -> Any:
        return getattr(self, item)


class Record(OneTaskBaseEntity):
    """
    Record Entity wrapping data imported in your project.

    :param custom_id: Identifier of the record.
    :param attributes: Dictionary containing the attributes defined in your records.
    :param annotation_list: List of the manual labels for this given record. This does NOT contain synthetic labels!
    :param embeddings: Dictionary containing the embeddings defined in your records.
    """

    def __init__(
            self,
            custom_id: str,
            attributes: Dict[str, Any],
            annotation_list: Optional[List[str]] = None,
            embeddings: Optional[Dict[str, np.array]] = None
    ):
        self.custom_id = custom_id
        self.annotation_list = annotation_list
        self.attributes = attributes
        if embeddings is None:
            embeddings = {}
        self.embeddings = embeddings


class NoisyRecordHit(OneTaskBaseEntity):
    """
    Entity wrapping data for a noisy record hit, i.e. hits of a labeling function on a record.

    :param custom_id: Identifier of the record.
    :param noisy_annotation_list: List of the labels which are hit for this record. These are noisy labels!
    """

    def __init__(
            self,
            custom_id: str,
            noisy_annotation_list: List[str]
    ):
        self.custom_id = custom_id
        self.noisy_annotation_list = noisy_annotation_list


class LFDefinition(OneTaskBaseEntity):
    """
    Entity containing static metadata for a labeling function that is not needed to execute the labeling function.

    :param body_type: Type of the labeling function body (subclass)
    :param description: Text explaining the function as in a docstring
    :param internal_id: Technical identification of the labeling function.
    """

    def __init__(
            self,
            body_type: str,
            description: Optional[str] = None,
            internal_id: Optional[str] = None,
    ):
        # client-defined
        self.description = description
        self.body_type = body_type

        # server-defined
        self.internal_id = internal_id


class LFBody(OneTaskBaseEntity):
    """
    Entitiy containing data of a labeling function that is needed to execute the labeling function.

    :param source_code: Code of the Python function object as a string.
    :param programming_language_version: Python version of the function object.
    """

    def __init__(
            self,
            source_code: str,
            programming_language_version: str = "3"
    ):
        self.source_code = source_code
        self.function_name = re.search(r'def (.*?)\(', source_code).group(1)
        self.programming_language_name = "python"
        self.programming_language_version = programming_language_version


class LabelingFunction:
    """
    Composite entity of an LF Body and LF Description.

    :param definition: onetask LFDefinition.
    :param body: onetask LFBody.
    """

    def __init__(
            self,
            definition: LFDefinition,
            body: LFBody
    ):

        self.definition = definition
        self.body = body

    def __iter__(self) -> Generator[Any, Tuple[str, Any], None]:
        for key in self.__dict__:
            yield key, getattr(self, key).__dict__

    def __repr__(self) -> str:
        return (
            f'{self.__module__}.{self.__class__.__name__}(\n'
            f'    definition={object_utils.create_representational_string(self.definition, indent_add=4)},\n'
            f'    body={object_utils.create_representational_string(self.body, indent_add=4)}\n'
            ')'
        )

    def __str__(self) -> str:
        return self.body.source_code.replace("\t", "    ")

    def __getitem__(self, item) -> Any:
        return getattr(self, item)

    def execute(self, record_list: List[Record]) -> List[NoisyRecordHit]:
        """
        Runs a list of records on the labeling function and returns their noisy record hits.

        :param record_list: List of onetask record entities.
        :return: List of onetask noisy record hit entities.
        """

        source_code = self.body.source_code
        function_name = self.body.function_name
        exec(source_code)
        processor = locals()[function_name]

        record_hit_list = []
        for record in record_list:
            hit_labels = processor(record)
            record_hit = NoisyRecordHit(custom_id=record.custom_id, noisy_annotation_list=hit_labels)
            record_hit_list.append(record_hit)
        return record_hit_list
