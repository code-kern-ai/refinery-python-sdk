import yaml
import os
from collections import OrderedDict

CONSTANT_OUTSIDE = "OUTSIDE"
CONSTANT_LABEL_BEGIN = "B-"
CONSTANT_LABEL_INTERMEDIATE = "I-"


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


def inject_label_in_text(row, text_name, tokenized_label_task, constant_outside):
    string = ""
    token_list = row[f"{text_name}__tokenized"]

    close_multitoken_label = False
    multitoken_label = False
    for idx, token in enumerate(token_list):

        if idx < len(token_list) - 1:
            token_next = token_list[idx + 1]
            label_next = row[tokenized_label_task][idx + 1]
            if label_next.startswith(CONSTANT_LABEL_INTERMEDIATE):
                multitoken_label = True
            else:
                if multitoken_label:
                    close_multitoken_label = True
                multitoken_label = False
            num_whitespaces = token_next.idx - (token.idx + len(token))
        else:
            num_whitespaces = 0
        whitespaces = " " * num_whitespaces

        label = row[tokenized_label_task][idx]
        if label != constant_outside:
            if multitoken_label:
                if label.startswith(CONSTANT_LABEL_BEGIN):
                    string += f"[{token.text}{whitespaces}"
                else:
                    string += f"{token.text}{whitespaces}"
            else:
                label_trimmed = label[2:]  # remove B- and I-
                if close_multitoken_label:
                    string += f"{token.text}]({label_trimmed}){whitespaces}"
                    close_multitoken_label = False
                else:
                    string += f"[{token.text}]({label_trimmed}){whitespaces}"
        else:
            string += f"{token.text}{whitespaces}"
    return string


def build_intent_yaml(
    client,
    text_name,
    intent_label_task,
    metadata_label_task=None,
    tokenized_label_task=None,
    dir_name="data",
    file_name="nlu.yml",
    constant_outside=CONSTANT_OUTSIDE,
):
    df = client.get_record_export(tokenize=(tokenized_label_task is not None))

    if tokenized_label_task is not None:
        text_name_injected = f"{text_name}__injected"
        df[text_name_injected] = df.apply(
            lambda x: inject_label_in_text(
                x, text_name, tokenized_label_task, constant_outside
            ),
            axis=1,
        )
        text_name = text_name_injected

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

    if tokenized_label_task is not None:

        def flatten(xss):
            return [x for xs in xss for x in xs]

        labels = set(flatten(df[tokenized_label_task].tolist()))
        lookup_list_names = []
        for label in labels:
            if label.startswith(CONSTANT_LABEL_BEGIN):
                label_trimmed = label[2:]  # remove B-
                lookup_list_names.append(label_trimmed)

        for lookup_list in client.get_lookup_lists():
            if lookup_list["name"] in lookup_list_names:
                values = [entry["value"] for entry in lookup_list["terms"]]
                literal_string = build_literal_from_iterable(values)
                nlu_list.append(
                    OrderedDict(
                        lookup=lookup_list["name"], examples=literal(literal_string)
                    )
                )

    nlu_dict = OrderedDict(nlu=nlu_list)

    if dir_name is not None and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    file_path = os.path.join(dir_name, file_name)

    with open(file_path, "w") as f:
        yaml.dump(nlu_dict, f, allow_unicode=True)
