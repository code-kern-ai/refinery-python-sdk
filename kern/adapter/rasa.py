import yaml
import os
from collections import OrderedDict


class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal, literal_presenter)


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


yaml.add_representer(OrderedDict, ordered_dict_presenter)


def build_literal_from_iterable(iterable):
    return "\n".join([f"- {value}" for value in iterable]) + "\n"


def build_intent_yaml(
    client,
    text_name,
    intent_label_task,
    metadata_label_task=None,
    dir_name="data",
    file_name="nlu.yml",
):
    df = client.get_record_export(tokenize=False)

    nlu_list = []
    for label, df_sub_label in df.groupby(intent_label_task):

        if metadata_label_task is not None:
            metadata_label_name = metadata_label_task.split("__")[1]
            for metadata_label, df_sub_label_sub_metadata_label in df_sub_label.groupby(
                metadata_label_task
            ):
                literal_string = build_literal_from_iterable(
                    df_sub_label_sub_metadata_label[text_name].tolist()
                )
                nlu_list.append(
                    OrderedDict(
                        intent=label,
                        metadata=OrderedDict(**{metadata_label_name: metadata_label}),
                        examples=literal(literal_string),
                    )
                )
        else:
            literal_string = build_literal_from_iterable(
                df_sub_label[text_name].tolist()
            )
            nlu_list.append(OrderedDict(intent=label, examples=literal(literal_string)))
    nlu_dict = OrderedDict(nlu=nlu_list)

    if dir_name is not None and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    file_path = os.path.join(dir_name, file_name)

    with open(file_path, "w") as f:
        yaml.dump(nlu_dict, f, allow_unicode=True)
