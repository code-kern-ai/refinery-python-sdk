from collections import defaultdict
from tqdm import tqdm
from collections import Counter
import re
from collections import defaultdict
import numpy as np
from wasabi import msg


def derive_regex_candidates(nlp, df, attribute, most_common=10):
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
        return not (token.is_punct or token.is_stop or token.is_bracket)

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
    return [regex for regex, _ in Counter(candidates).most_common(most_common)]


def create_regex_fns(df, candidates, regex_col, label_col="manual_label"):
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
                    description += f" followed by term '{term}'"
        if "[0-9]" in regex:
            description += ", where [0-9] is an arbitrary number"
        description += "."
        return description

    def build_regex_lf(regex, attribute, prediction, iteration):
        source_code = f"""
def regex_{iteration}(record):
    '''{regex_explainer(regex, attribute)}'''
    import re
    if re.search(r'{regex}', record['{attribute}'].lower()):
        return '{prediction}'

client.register_lf(regex_{iteration})
        """

        return source_code.strip()

    regex_nr = 1
    for regex in candidates:
        labels = defaultdict(int)
        for text, label in zip(df[regex_col], df[label_col]):
            if re.search(regex, text.lower()):
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
            if precision > 0.75 and coverage >= 0.01:
                lf = build_regex_lf(regex, regex_col, regex_prediction, regex_nr)
                regex_nr += 1
                print(f"# Cov:\t{coverage}\tPrec:{precision}")
                print(lf)
                print()
