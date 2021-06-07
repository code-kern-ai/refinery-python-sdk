from typing import List

import pandas as pd

from onetask import entities


def attributes_df_from_records(record_list: List[entities.Record]) -> pd.DataFrame:
    """
    Creates a pandas DataFrame containing the flattened attributes as columns with the custom id as the index.

    :param record_list: List of onetask Record entities.
    :return: pandas DataFrame.
    """

    index_list = []
    attributes_list = []

    for record in record_list:
        index_list.append(record.custom_id)
        attributes_list.append(record.attributes)

    df = pd.json_normalize(attributes_list)
    df.index = index_list

    return df
