import os
from wasabi import msg
from typing import Any, List, Optional
import pandas as pd
import yaml
from refinery import Client, exceptions
from collections import OrderedDict

# https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal, literal_presenter)


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


yaml.add_representer(OrderedDict, ordered_dict_presenter)

CONSTANT_OUTSIDE = "OUTSIDE"
CONSTANT_LABEL_BEGIN = "B-"
CONSTANT_LABEL_INTERMEDIATE = "I-"


def build_literal_from_iterable(iterable: List[Any]) -> str:
    """Builds a Rasa-conform yaml string from an iterable.

    Args:
        iterable (List[Any]): List with values to be converted to a literal block.

    Returns:
        str: literal block
    """
    return "\n".join([f"- {value}" for value in iterable]) + "\n"


def inject_label_in_text(
    row: pd.Series, text_name: str, tokenized_label_task: str, constant_outside: str
) -> str:
    """Insert token labels into text.
    E.g. "Hello, my name is Johannes Hötter" -> "Hello, my name is [Johannes Hötter](person)"

    Args:
        row (pd.Series): row of the record export dataframe
        text_name (str): name of the text/chat field
        tokenized_label_task (str): name of the label task containing token-level labels
        constant_outside (str): constant to be used for outside labels

    Returns:
        str: injected text
    """
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
    client: Client,
    text_name: str,
    intent_label_task: str,
    metadata_label_task: Optional[str] = None,
    tokenized_label_task: Optional[str] = None,
    dir_name: str = "data",
    file_name: str = "nlu.yml",
    constant_outside: str = CONSTANT_OUTSIDE,
    version: str = "3.1",
) -> None:
    """builds a Rasa NLU yaml file from your project data via the client object.

    Args:
        client (Client): connected Client object for your project
        text_name (str): name of the text/chat field
        intent_label_task (str): name of the classification label with the intents
        metadata_label_task (Optional[str], optional): if you have a metadata task (e.g. sentiment), you can list it here. Currently, only one is possible to provide. Defaults to None.
        tokenized_label_task (Optional[str], optional): if you have a token-level task (e.g. for entities), you can list it here. Currently, only one is possible to provide. Defaults to None.
        dir_name (str, optional): name of your rasa data directory. Defaults to "data".
        file_name (str, optional): name of the file you want to store the data to. Defaults to "nlu.yml".
        constant_outside (str, optional): constant to be used for outside labels in token-level tasks. Defaults to CONSTANT_OUTSIDE.
        version (str, optional): Rasa version. Defaults to "3.1".

    Raises:
        exceptions.UnknownItemError: if the item you are looking for is not found.
    """
    msg.info("Building training data for Rasa")
    msg.warn("If you haven't done so yet, please install rasa and run `rasa init`")
    df = client.get_record_export(tokenize=(tokenized_label_task is not None))

    for attribute in [text_name, intent_label_task, metadata_label_task, tokenized_label_task]:
        if attribute is not None and attribute not in df.columns:
            raise exceptions.UnknownItemError(f"Can't find argument '{attribute}' in the existing export schema: {df.columns.tolist()}")

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

    nlu_dict = OrderedDict(version=version, nlu=nlu_list)

    if dir_name is not None and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    file_path = os.path.join(dir_name, file_name)

    with open(file_path, "w") as f:
        yaml.dump(nlu_dict, f, allow_unicode=True)
        msg.good(f"Saved training data to {file_path}! 🚀")
        msg.warn(
            f"Please make sure to add the project-specific files domain.yml, {os.path.join(dir_name, 'rules.yml')} and {os.path.join(dir_name, 'stories.yml')}."
        )
        msg.info("More information about these files can be found here:")
        msg.info(" - Domain: https://rasa.com/docs/rasa/domain")
        msg.info(" - Rules: https://rasa.com/docs/rasa/rules")
        msg.info(" - Stories: https://rasa.com/docs/rasa/stories")
        msg.good(
            "You're all set, and can now start building your conversational AI via `rasa train`! 🎉"
        )
