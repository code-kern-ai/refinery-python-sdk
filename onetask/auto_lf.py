# -*- coding: utf-8 -*-
from collections import defaultdict
from tqdm import tqdm
from collections import Counter
import re
from collections import defaultdict
import numpy as np
import pandas as pd
from wasabi import msg


def derive_regex_candidates(nlp, df, attribute, filter_stopwords):
    if len(df) < 100:
        msg.warn(
            "Only very few records to analyze; it's best to continue labeling further records before analysis"
        )

    def normalize_token(token):
        if "d" in token.shape_ and not "x" in token.shape_:
            return token.shape_.replace("d", "[0-9]")
        else:
            return token.text

    def is_relevant_token(token):
        conditions = [token.is_punct, token.is_bracket, len(token.text) == 1]
        if filter_stopwords:
            conditions.append(token.is_stop)
        return not any(conditions)

    candidates = []
    for text in tqdm(df[attribute], total=len(df)):
        doc = nlp(text.lower())
        for token in doc:
            if is_relevant_token(token):
                has_children = False
                for token_left in token.lefts:
                    if is_relevant_token(token_left):
                        prefix = "^" if token_left.idx == 0 else " "
                        suffix = "$" if token.idx == len(doc) - 1 else " "
                        candidate = f"{prefix}{normalize_token(token_left)}.*?{normalize_token(token)}{suffix}"
                        candidates.append(candidate)
                        has_children = True
                for token_right in token.rights:
                    if is_relevant_token(token_right):
                        prefix = "^" if token.idx == 0 else " "
                        suffix = "$" if token_right.idx == len(doc) - 1 else " "
                        candidate = f"{prefix}{normalize_token(token)}.*?{normalize_token(token_right)}{suffix}"
                        candidates.append(candidate)
                        has_children = True
                if not has_children:
                    prefix = "^" if token.idx == 0 else " "
                    suffix = "$" if token.idx == len(doc) - 1 else " "
                    candidate = f"{prefix}{normalize_token(token)}{suffix}"
                    candidates.append(candidate)
    return [regex for regex, _ in Counter(candidates).most_common(100)]


def create_regex_fns(df, candidates, regex_col, min_precision, label_col="label"):
    n = len(df)

    def calc_min_cov(x):
        return 0.3 / (x ** 0.5)

    min_coverage = calc_min_cov(n)

    def regex_explainer(regex, attribute):
        description = ""
        terms = regex.replace("^", "").replace("$", "").split(".*?")
        if "^" in regex:
            description += f"attribute '{attribute}' starts with term '{terms[0]}'"
            if len(terms) > 1:
                for term in terms[1:]:
                    description += f" (in-)directly  followed by term '{term}'"
            if "$" in regex:
                description += " and then ends"
        elif "$" in regex:
            description += (
                f"attribute '{attribute}' somewhere contains term '{terms[0]}'"
            )
            if len(terms) > 1:
                for term in terms[1:]:
                    description += f" (in-)directly followed by term '{term}'"
            description += " and then ends"
        else:
            description += (
                f"attribute '{attribute}' somewhere contains term '{terms[0]}'"
            )
            if len(terms) > 1:
                for term in terms[1:]:
                    description += f" (in-)directly followed by term '{term}'"
        if "[0-9]" in regex:
            description += ", where [0-9] is an arbitrary number"
        description += "."
        return description

    def build_regex_lf(regex, attribute, prediction, iteration, escape_regex):

        if escape_regex:
            _regex = f"re.escape('{regex}')"
        else:
            _regex = f"r'{regex}'"
        source_code = f"""
def regex_{iteration}(record):
    '''{regex_explainer(regex, attribute)}'''
    import re
    if re.search({_regex}, record['{attribute}'].lower()):
        return '{prediction}'

client.register_lf(regex_{iteration})
        """

        return source_code.strip()

    regex_nr = 1
    rows = []
    for regex in candidates:
        labels = defaultdict(int)
        escape_regex = False
        for text, label in zip(df[regex_col], df[label_col]):
            try:
                if re.search(regex, text.lower()):
                    labels[label] += 1
            except:  # there is sadly no better way (I know of) to handle this other than using a plain except
                escape_regex = True
                if re.search(re.escape(regex), text.lower()):
                    labels[label] += 1
        coverage = sum(labels.values())
        if coverage > 0:
            regex_prediction, max_count = None, 0
            for prediction, count in labels.items():
                if count > max_count:
                    max_count = count
                    regex_prediction = prediction
            precision = np.round(labels[regex_prediction] / coverage, 2)
            coverage = np.round(coverage / len(df), 2)
            if precision >= min_precision and coverage >= min_coverage:
                lf = build_regex_lf(
                    regex, regex_col, regex_prediction, regex_nr, escape_regex
                )
                regex_nr += 1
                rows.append(
                    {
                        "est_coverage": coverage,
                        "est_precision": precision,
                        "label": regex_prediction,
                        "code": lf,
                    }
                )
    lf_df = pd.DataFrame(rows)
    lf_df["priority"] = (lf_df["est_coverage"] ** 2) * lf_df["est_precision"]
    lf_df = lf_df.sort_values(by="priority", ascending=False)
    return lf_df
