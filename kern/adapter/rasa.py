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
    client, input_name, label_name, dir_name="data", file_name="nlu.yml"
):
    df = client.get_record_export(tokenize=False)

    nlu_list = []
    for label, df_label in df.groupby(label_name):
        literal_string = build_literal_from_iterable(df_label[input_name].tolist())
        nlu_list.append(OrderedDict(intent=label, examples=literal(literal_string)))
    nlu_dict = OrderedDict(nlu=nlu_list)

    if dir_name is not None and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    file_path = os.path.join(dir_name, file_name)

    with open(file_path, "w") as f:
        yaml.dump(nlu_dict, f, allow_unicode=True)
