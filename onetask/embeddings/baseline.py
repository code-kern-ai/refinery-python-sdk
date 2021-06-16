# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.preprocessing import LabelBinarizer

CHAR_SET = [chr(idx) for idx in range(32, 127)]
char_lookup = {char: idx for idx, char in enumerate(CHAR_SET)}
SEP = "_"


def get_baseline_embedding(
        attribute_dict_list: List[Dict[str, Any]], attributes_schema: Dict[str, Dict[str, str]]
) -> Tuple[np.array, np.array]:
    """

    :param attribute_dict_list:
    :param attributes_schema:
    :return:
    """

    all_values_by_attribute_dict = {
        attribute["path"]: []
        for attribute in attributes_schema
    }

    for row_id, record in enumerate(attribute_dict_list):
        for attribute, value in record.items():
            all_values_by_attribute_dict[attribute].append(value)

    feature_names = []
    feature_matrix = []
    for attribute in attributes_schema:
        path = attribute["path"]
        values = all_values_by_attribute_dict[path]
        if attribute["type"] == "string":
            bag_of_chars = []
            for sentence in values:
                char_vector = np.zeros(len(CHAR_SET))
                for char in sentence:
                    try:
                        char_vector[char_lookup[char]] += 1
                    except KeyError:
                        pass
                bag_of_chars.append(char_vector)
            bag_of_chars = np.array(bag_of_chars)
            feature_names.extend([f"{path}{SEP}{name}" for name in CHAR_SET])
            feature_matrix.append(bag_of_chars)
        elif attribute["type"] == "category":
            binarizer = LabelBinarizer()
            one_hot_encodings = binarizer.fit_transform(values)
            feature_names.extend([f"{path}{SEP}{name}" for name in binarizer.classes_])
            feature_matrix.append(one_hot_encodings)
        elif attribute["type"] == "number":
            feature_names.extend([f"{path}{SEP}"])
            feature_matrix.append(np.expand_dims(values, axis=-1))
        elif attribute["type"] == "boolean":
            feature_names.extend([f"{path}{SEP}"])
            feature_matrix.append(np.expand_dims(values, axis=-1))

    feature_matrix = np.asarray(np.concatenate(feature_matrix, axis=1)).tolist()
    feature_names = np.asarray(feature_names)

    return feature_matrix, feature_names
