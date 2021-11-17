[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# onetask API for Python

Official Python SDK for onetask.

## Installation

You can use pip to install the library:

`$ pip install onetask`

Alternatively, you can clone the repository and run the setup.py script:

`$ python setup.py install`

## Usage

The SDK currently offers the following functions:
- registering local Python functions as labeling functions in our system (you can of course also develop such functions within our web system)
- _experimental_: generating embeddings for your attributes, e.g. free texts or structured data containing categories and numbers
- _experimental_: autogenerating labeling functions from manually labeled records in your project
- _experimental_: topic modeling using BERT embeddings that you have registered in your project

All of this is also documented in the [onetask Documentation](https://onetask.readme.io/reference/getting-started), with additional screenshots to guide you through the process.


### Instantiating a Client object

You begin by creating a `Client` object. The `Client` will generate and store a session token for you based on your user name, password, and project id. The project id can be found in the URL, e.g. https://app.beta.onetask.ai/app/projects/**03f7d82c-f14c-4f0f-a1ff-59533bab30cc**/overview. Simply copy and paste this into the following pattern:

```python
from onetask import Client

username = "your-username"
password = "your-password"
project_id = "your-project-id"
stage = "beta" # if you have onetask on local, you can also set stage to "local"
client = Client(username, password, project_id, stage)
```

Once you correctly instantiated your Client, you can start using it for the various functions provided in the SDK. 


### Registering local Python labeling functions

You can register functions e.g. from your local Jupyter Notebook using our SDK. When doing so, please always ensure that your labeling functions:
- return label names that also exist in your project definition
- have exactly one parameter; we execute labeling functions on a record-basis
- If you need an import statement in your labeling functions, please check if it is given in the [whitelisted libraries](https://onetask.readme.io/reference/whitelisted-libraries). If you need a library that we have not yet whitelisted, feel free to reach out to us.

An example to register your custom labeling function is as follows:
```python
def my_labeling_function(record):
  """
  Detect a list of values in the records that tend to occur in urgent messages.
  """
  keywords = ["asap", "as soon as possible", "urgent"]
  
  message_lower = record["message"].lower()
  for keyword in keywords:
    if keyword in message_lower:
      return "Urgent"
```

You can then enter them using the client:

```python
client.register_lf(my_labeling_function)
```

The labeling function is then automatically executed once registered, where you can always change and re-run it.

### Generating embeddings (experimental)

One of the main features of onetask is to apply both Weak Supervision and Active Learning jointly. To build the best possible Active Learning Weak Sources, you can generate embeddings for your attributes using the SDK. To do so, you have to first upload your data in our web application and select a unique attribute (see our [documentation](https://onetask.readme.io/reference/create-your-project) for further reference on how to set this up).

Once this is done, you can easily generate embedding files. Imagine you have the following attributes in your records:
- `headline`: an english text describing e.g. the news of a paper (e.g. _"5 footballers that should have won the ballon d'or"_, ...)
- `running_id`: a unique identifier for each headline, i.e. a simple number (e.g. 1, 2, 3, ...)

You can then call the client object to generate an embedding file using a dictionary of attribute/configuration string pairs:
```python
client.generate_embeddings({"headline": "distilbert-base-uncased"})
```

This will generate an embedding JSON-file as follows:

```json
[
  {
    "running_id": 1,
    "distilbert-base-uncased": [0.123456789, "..."]
  },
  {
    "running_id": 2,
    "distilbert-base-uncased": [0.234567891, "..."]
  },
]
```

You can upload this file to your project in the overview tab of your project.

The following configuration strings are available to configure how your attributes are embedded:
| Configuration String | Data Type                     | Explanation                                                                                  |
|----------------------|-------------------------------|----------------------------------------------------------------------------------------------|
| identity             | integer, float                | No transformation                                                                            |
| onehot               | category (low-entropy string) | one-hot encodes attribute                                                                    |
| bow                  | string                        | Bag of Words transformation                                                                  |
| boc                  | string                        | Bag of Characters transformation                                                             |
| _huggingface_        | string                        | Huggingface-based transformation. You can use any available [huggingface](https://huggingface.co/) configuration string |

If you want to embed multiple attributes (which makes sense e.g. when you have structured data), you can provide multiple key/value pairs in your input dictionary. The resulting embeddings will be concatenated into one vector.


### Autogenerating labeling functions (experimental)

As you manually label data, onetask can help you to analyze both the explicitic and implicit data patterns. Our first approach for explicit pattern detection is to find regular expressions in free text attributes you provide. They are being mined using linguistic analysis, therefore you need to provide a spacy nlp object for the respective language of your free text.

If you have an english free text, you can implement the mining as follows:
```python
import spacy # you need to also download the en_core_web_sm file using $ python -m spacy download en_core_web_sm

nlp = spacy.load("en_core_web_sm")
lf_df = client.generate_regex_labeling_functions(nlp, "headline")
```

This creates a DataFrame containing mined regular expressions. You can display them in a convenient way:

```python
client.display_generated_labeling_functions(lf_df)
```

**Caution**: The quality and quantity of mined regular expressions heavily depends on how much data you have labeled and how diverse your dataset is. We have tested the feature on various datasets and found it to be very helpful. If you have problems autogenerating labeling functions in your project, contact us.


### Topic Modeling using BERT embeddings (experimental)

As onetask lets you put insights of explorative analysis into programmatic data labeling, we also provide topic modeling. We use the [BERTopic](https://github.com/MaartenGr/BERTopic) library for topic modeling, and provide an easy access to your projects data and embeddings. Once you uploaded BERT embeddings to your project (such that can be created using a huggingface configuration string), you can create a topic model:

```python
topic_model = client.model_topics("headline", "distilbert-base-uncased")
```

The `topic_model` provides various methods to explore the different keywords and topics. You can also find further documentation [here](https://maartengr.github.io/BERTopic/api/bertopic.html).

## Outlook and Feature Requests
In the near future, we'll extend the Python SDK to include programmatic imports and exports, data access, and many more. If you have any requests, feel free to [contact us](https://www.onetask.ai/contact-us).

## Support
If you need help, feel free to join our Slack Community channel. It is currently only available via invitation.
