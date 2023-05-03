[![refinery repository](https://uploads-ssl.webflow.com/61e47fafb12bd56b40022a49/62cf1c3cb8272b1e9c01127e_refinery%20sdk%20banner.png)](https://github.com/code-kern-ai/refinery)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![pypi 1.4.0](https://img.shields.io/badge/pypi-1.4.0-yellow.svg)](https://pypi.org/project/refinery-python-sdk/1.4.0/)

This is the official Python SDK for [*refinery*](https://github.com/code-kern-ai/refinery), the **open-source** data-centric IDE for NLP.

**Table of Contents**
- [Installation](#installation)
- [Usage](#usage)
  - [Creating a `Client` object](#creating-a-client-object)
  - [Fetching labeled data](#fetching-labeled-data)
  - [Fetching lookup lists](#fetching-lookup-lists)
  - [Upload files](#upload-files)
  - [Adapters](#adapters)
    - [Sklearn](#sklearn-adapter)
    - [PyTorch](#pytorch-adapter)
    - [HuggingFace](#hugging-face-adapter)
    - [Rasa](#rasa-adapter)
  - [Callbacks](#callbacks)
    - [Sklearn](#sklearn-callback)
    - [PyTorch](#pytorch-callback)
    - [HuggingFace](#hugging-face-callback)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

If you like what we're working on, please leave a ⭐!

## Installation

You can set up this SDK either via running `$ pip install refinery-python-sdk`, or by cloning this repository and running `$ pip install -r requirements.txt`.

## Usage

### Creating a `Client` object
Once you installed the package, you can create a `Client` object from any Python terminal as follows:

```python
from refinery import Client

user_name = "your-username" # this is the email you log in with
password = "your-password"
project_id = "your-project-id" # can be found in the URL of the web application

client = Client(user_name, password, project_id)
# if you run the application locally, please use the following instead:
# client = Client(user_name, password, project_id, uri="http://localhost:4455")
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

Alternatively, you can also just run `rsdk pull` in your CLI given that you have provided the `secrets.json` file in the same directory.

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

### Fetching lookup lists
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

We use Pandas to process the data you upload, so you can also provide `import_file_options` for the file type you use. Currently, you need to provide them as a `\n`-separated string (e.g. `"quoting=1\nsep=';'"`). We'll adapt this in the future to work with dictionaries instead.

Alternatively, you can `rsdk push <path-to-your-file>` via CLI, given that you have provided the `secrets.json` file in the same directory.

**Make sure that you've selected the correct project beforehand, and fit the data schema of existing records in your project!**

### Adapters

#### Sklearn Adapter
You can use *refinery* to directly pull data into a format you can apply for building [sklearn](https://github.com/scikit-learn/scikit-learn) models. This can look as follows:

```python
from refinery.adapter.sklearn import build_classification_dataset
from sklearn.tree import DecisionTreeClassifier

data = build_classification_dataset(client, "headline", "__clickbait", "distilbert-base-uncased")

clf = DecisionTreeClassifier()
clf.fit(data["train"]["inputs"], data["train"]["labels"])

pred_test = clf.predict(data["test"]["inputs"])
accuracy = (pred_test == data["test"]["labels"]).mean()
```

By the way, we can highly recommend to combine this with [Truss](https://github.com/basetenlabs/truss) for easy model serving!

#### PyTorch Adapter
If you want to build a [PyTorch](https://github.com/pytorch/pytorch) network, you can build the `train_loader` and `test_loader` as follows:

```python
from refinery.adapter.torch import build_classification_dataset
train_loader, test_loader, encoder, index = build_classification_dataset(
    client, "headline", "__clickbait", "distilbert-base-uncased"
)
```

#### Hugging Face Adapter
Transformers are great, but often times, you want to finetune them for your downstream task. With *refinery*, you can do so easily by letting the SDK build the dataset for you that you can use as a plug-and-play base for your training:

```python
from refinery.adapter import transformers
dataset, mapping, index = transformers.build_classification_dataset(client, "headline", "__clickbait")
```

From here, you can follow the [finetuning example](https://huggingface.co/docs/transformers/training) provided in the official Hugging Face documentation. A next step could look as follows:

```python
small_train_dataset = dataset["train"].shuffle(seed=42).select(range(1000))
small_eval_dataset = dataset["test"].shuffle(seed=42).select(range(1000))

from transformers import (
  AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
)
import numpy as np
from datasets import load_metric

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize_function(examples):
    return tokenizer(examples["headline"], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
training_args = TrainingArguments(output_dir="test_trainer")
metric = load_metric("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

training_args = TrainingArguments(output_dir="test_trainer", evaluation_strategy="epoch")

small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

trainer.save_model("path/to/model")
```

#### Rasa Adapter
*refinery* is perfect to be used for building chatbots with [Rasa](https://github.com/RasaHQ/rasa). We've built an adapter with which you can easily create the required Rasa training data directly from *refinery*.

To do so, do the following:

```python
from refinery.adapter import rasa

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
from refinery.adapter import rasa

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
from refinery.adapter import rasa

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


### Callbacks
If you want to feed your production model's predictions back into *refinery*, you can do so with any version greater than [1.2.1](https://github.com/code-kern-ai/refinery/releases/tag/v1.2.1).

To do so, we have a generalistic interface and framework-specific classes.

#### Sklearn Callback
If you want to train a scikit-learn model an feed its outputs back into the refinery, you can do so easily as follows:

```python
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression() # we use this as an example, but you can use any model implementing predict_proba

from refinery.adapter.sklearn import build_classification_dataset
data = build_classification_dataset(client, "headline", "__clickbait", "distilbert-base-uncased")
clf.fit(data["train"]["inputs"], data["train"]["labels"])

from refinery.callbacks.sklearn import SklearnCallback
callback = SklearnCallback(
    client, 
    clf,
    "clickbait", 
)

# executing this will call the refinery API with batches of size 32, so your data is pushed to the app
callback.run(data["train"]["inputs"], data["train"]["index"])
callback.run(data["test"]["inputs"], data["test"]["index"])
```

#### PyTorch Callback
For PyTorch, the procedure is really similar. You can do as follows:

```python
from refinery.adapter.torch import build_classification_dataset
train_loader, test_loader, encoder, index = build_classification_dataset(
    client, "headline", "__clickbait", "distilbert-base-uncased"
)

# build your custom model and train it here - example:
import torch.nn as nn
import numpy as np
import torch

# number of features (len of X cols)
input_dim = 768
# number of hidden layers
hidden_layers = 20
# number of classes (unique of y)
output_dim = 2
class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.linear1 = nn.Linear(input_dim, output_dim)
   
    def forward(self, x):
        x = torch.sigmoid(self.linear1(x))
        return x
    
clf = Network()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(clf.parameters(), lr=0.1)

epochs = 2
for epoch in range(epochs):
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        # set optimizer to zero grad to remove previous epoch gradients
        optimizer.zero_grad()
        # forward propagation
        outputs = clf(inputs)
        loss = criterion(outputs, labels)
        # backward propagation
        loss.backward()
        # optimize
        optimizer.step()
        running_loss += loss.item()
        # display statistics
        print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.5f}')
        running_loss = 0.0

# with this model trained, you can use the callback
from refinery.callbacks.torch import TorchCallback
callback = TorchCallback(
    client, 
    clf,
    "clickbait", 
    encoder
)

# and just execute this 
callback.run(train_loader, index["train"])
callback.run(test_loader, index["test"])
```

#### HuggingFace Callback
Collect the dataset and train your custom transformer model as follows:

```python
from refinery.adapter import transformers
dataset, mapping, index = transformers.build_classification_dataset(client, "headline", "__clickbait")

# train a model here, we're simplifying this by just using an existing model w/o retraining
from transformers import pipeline
pipe = pipeline("text-classification", model="distilbert-base-uncased")

# if you're interested to see how a training looks like, look into the above HuggingFace adapter

# you can now apply the callback
from refinery.callbacks.transformers import TransformerCallback
callback = TransformerCallback(
    client, 
    pipe,
    "clickbait", 
    mapping
)

callback.run(dataset["train"]["headline"], index["train"])
callback.run(dataset["test"]["headline"], index["test"])
```

#### Generic Callback
This one is your fallback if you have a very custom solution; other than that, we recommend you look into the framework-specific classes.

```python
from refinery.callbacks.inference import ModelCallback
from refinery.adapter.sklearn import build_classification_dataset
from sklearn.linear_model import LogisticRegression

data = build_classification_dataset(client, "headline", "__clickbait", "distilbert-base-uncased"0)
clf = LogisticRegression()
clf.fit(data["train"]["inputs"], data["train"]["labels"])

# you can build initialization functions that set states of objects you use in the pipeline
def initialize_fn(inputs, labels, **kwargs):
    return {"clf": kwargs["clf"]}

# postprocessing shifts the model outputs into a format accepted by our API
def postprocessing_fn(outputs, **kwargs):
    named_outputs = []
    for prediction in outputs:
        pred_index = prediction.argmax()
        label = kwargs["clf"].classes_[pred_index]
        confidence = prediction[pred_index]
        named_outputs.append([label, confidence])
    return named_outputs

callback = ModelCallback(
    client: Client,
    "my-custom-regression",
    "clickbait",
    inference_fn=clf.predict_proba,
    initialize_fn=initialize_fn,
    postprocessing_fn=postprocessing_fn
)

# executing this will call the refinery API with batches of size 32
callback.initialize_and_run(data["train"]["inputs"], data["train"]["index"])
callback.run(data["test"]["inputs"], data["test"]["index"])
```


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
This library is developed and maintained by [Kern AI](https://github.com/code-kern-ai). If you want to provide us with feedback or have some questions, don't hesitate to contact us. We're super happy to help ✌️
