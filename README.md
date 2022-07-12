![kern-python](https://uploads-ssl.webflow.com/61e47fafb12bd56b40022a49/62766400bd3c57b579d289bf_kern-python%20Banner.png)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![pypi 0.0.4](https://img.shields.io/badge/pypi-0.0.4-yellow.svg)](https://pypi.org/project/kern-sdk/0.0.4/)

# Kern AI API for Python

This is the official Python SDK for [*refinery*](https://github.com/code-kern-ai/refinery), your **open-source** data-centric IDE for NLP.

## Installation

You can set up this SDK either via running `$ pip install kern-sdk`, or by cloning this repository and running `$ pip install -r requirements.txt`.

## Usage

### Creating a `Client` object
Once you installed the package, you can create a `Client` object from any Python terminal as follows:

```python
from kern import Client

user_name = "your-username"
password = "your-password"
project_id = "your-project-id" # can be found in the URL of the web application

client = Client(user_name, password, project_id)
# if you run the application locally, please use the following instead:
# client = Client(username, password, project_id, uri="http://localhost:4455")
```

The `project_id` can be found in your browser, e.g. if you run the app on your localhost: `http://localhost:4455/app/projects/{project_id}/overview`

Alternatively, you can provide a `secrets.json` file in your directory where you want to run the SDK, looking as follows:
```json
{
    "user_name": "your-username",
    "password": "your-password",
    "project_id": "your-project-id"
}
```

Again, if you run on your localhost, you should also provide `"uri": "http://localhost:4455"`. Afterwards, you can access the client like this:

```python
client = Client.from_secrets_file("secrets.json")
```

With the `Client`, you easily integrate your data into any kind of system; may it be a custom implementation, an AutoML system or a plain data analytics framework 🚀

### Fetching labeled data

Now, you can easily fetch the data from your project:
```python
df = client.get_record_export(tokenize=False)
# if you set tokenize=True (default), the project-specific 
# spaCy tokenizer will process your textual data
```

Alternatively, you can also just run `kern pull` in your CLI given that you have provided the `secrets.json` file in the same directory.

The `df` contains both your originally uploaded data (e.g. `headline` and `running_id` if you uploaded records like `{"headline": "some text", "running_id": 1234}`), and a triplet for each labeling task you create. This triplet consists of the manual labels, the weakly supervised labels, and their confidence. For extraction tasks, this data is on token-level.

An example export file looks like this:
```json
[
  {
    "running_id": "0",
    "Headline": "T. Rowe Price (TROW) Dips More Than Broader Markets",
    "Date": "Jun-30-22 06:00PM\u00a0\u00a0",
    "Headline__Sentiment Label__MANUAL": null,
    "Headline__Sentiment Label__WEAK_SUPERVISION": "Negative",
    "Headline__Sentiment Label__WEAK_SUPERVISION__confidence": "0.6220"
  }
]
```

In this example, there is no manual label, but a weakly supervised label `"Negative"` has been set with 62.2% confidence.

### Fetch lookup lists
In your project, you can create lookup lists to implement distant supervision heuristics. To fetch your lookup list(s), you can either get all or fetch one by its list id.
```python
list_id = "your-list-id"
lookup_list = client.get_lookup_list(list_id)
```

The list id can be found in your browser URL when you're on the details page of a lookup list, e.g. when you run on localhost: `http://localhost:4455/app/projects/{project_id}/knowledge-base/{list_id}`.

Alternatively, you can pull all lookup lists:
```python
lookup_lists = client.get_lookup_lists()
```

### Upload files
You can import files directly from your machine to your application:

```python
file_path = "my/file/path/data.json"
upload_was_successful = client.post_file_import(file_path)
```

Alternatively, you can `kern push <path-to-your-file>` via CLI, given that you have provided the `secrets.json` file in the same directory.

**Make sure that you've selected the correct project beforehand, and fit the data schema of existing records in your project!**

### Adapters

#### Rasa
*refinery* is perfect to be used for building chatbots with [Rasa](https://github.com/RasaHQ/rasa). We've built an adapter with which you can easily create the required Rasa training data directly from *refinery*.

To do so, do the following:

```python
from kern.adapter import rasa

rasa.build_intent_yaml(
  client,
  "text",
  "__intent__WEAK_SUPERVISION"
)
```

This will create a `.yml` file looking as follows:

```yml
nlu:
- intent: check_balance
  examples: |
    - how much do I have on my savings account
    - how much money is in my checking account
    - What's the balance on my credit card account
```

If you want to provide a metadata-level label (such as sentiment), you can provide the optional argument `metadata_label_task`:

```python
from kern.adapter import rasa

rasa.build_intent_yaml(
  client,
  "text",
  "__intent__WEAK_SUPERVISION",
  metadata_label_task="__sentiment__WEAK_SUPERVISION"
)
```

This will create a file like this:
```yml
nlu:
- intent: check_balance
  metadata:
    sentiment: neutral
  examples: |
    - how much do I have on my savings account
    - how much money is in my checking account
    - What's the balance on my credit card account
```

And if you have entities in your texts which you'd like to recognize, simply add the `tokenized_label_task` argument:

```python
from kern.adapter import rasa

rasa.build_intent_yaml(
  client,
  "text",
  "__intent__WEAK_SUPERVISION",
  metadata_label_task="__sentiment__WEAK_SUPERVISION",
  tokenized_label_task="text__entities__WEAK_SUPERVISION"
)
```

This will not only inject the label names on token-level, but also creates lookup lists for your chatbot:

```yml
nlu:
- intent: check_balance
  metadata:
    sentiment: neutral
  examples: |
    - how much do I have on my [savings](account) account
    - how much money is in my [checking](account) account
    - What's the balance on my [credit card account](account)
- lookup: account
  examples: |
    - savings
    - checking
    - credit card account
```

Please make sure to also create the further necessary files (`domain.yml`, `data/stories.yml` and `data/rules.yml`) if you want to train your Rasa chatbot. For further reference, see their [documentation](https://rasa.com/docs/rasa).

### What's missing?
Let us know what open-source/closed-source NLP framework you are using, for which you'd like to have an adapter implemented in the SDK. To do so, simply create an issue in this repository with the tag "enhancement".


## Roadmap
- [ ] Register heuristics via wrappers
- [ ] Up/download zipped projects for versioning via DVC
- [x] Add project upload
- [x] Fetch project statistics


If you want to have something added, feel free to open an [issue](https://github.com/code-kern-ai/kern-python/issues).

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

And please don't forget to leave a ⭐ if you like the work! 

## License
Distributed under the MIT License. See LICENSE.txt for more information.

## Contact
This library is developed and maintained by [kern.ai](https://github.com/code-kern-ai). If you want to provide us with feedback or have some questions, don't hesitate to contact us. We're super happy to help ✌️
