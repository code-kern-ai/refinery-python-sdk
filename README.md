[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# onetask API for Python

Official Python SDK for onetask.

## [](https://github.com/onetask-ai/onetask-python#installation)Installation

You can use pip to install the library:

`$ pip install onetask`

Alternatively, you can just clone the repository and run the setup.py script:

`$ python setup.py install`

## [](https://github.com/onetask-ai/onetask-python#usage)Usage

Before making requests to the API, you need to create an instance of the onetask client. You will have to use your  account API key:

```python
from onetask import Client
# Instantiate the client Using your API key
api_token = '<YOUR API TOKEN HERE>'
project_id = '<YOUR PROJECT ID HERE>'
client = Client(api_token=api_token, project_id=project_id)

# if you print the client, you will receive some further instructions
print(client)
```

There are several ways how you can start using our SDK. We'll show them in the following order:
1. [Fetching Sample Records](https://github.com/onetask-ai/onetask-python#fetching-sample-records)
2. [Writing Labeling Functions](https://github.com/onetask-ai/onetask-python#writing-labeling-functions)
3. [Testing Labeling Functions Locally](https://github.com/onetask-ai/onetask-python#testing-labeling-functions-locally)
4. [Registering Labeling Functions](https://github.com/onetask-ai/onetask-python#registering-labeling-functions)
5. [Fetching Labeling Functions](https://github.com/onetask-ai/onetask-python#fetching-labeling-functions)

### [](https://github.com/onetask-ai/onetask-python#fetching-sample-records)Fetching Sample Records

```python
max_number_samples = 100 # default value
record_list = client.get_all_records(max_number_samples=max_number_samples)
```

### [](https://github.com/onetask-ai/onetask-python#writing-labeling-functions)Writing Labeling Functions

Once you correctly instantiated your Client, you can start accessing record and labeling function endpoints. 
Please **always** ensure that your labeling functions:
- return label names that also exist in your project definition
- have exactly one parameter; we execute labeling functions on a record-basis
- If you need an import statement in your labeling functions, please check if it is given in the whitelisted libraries. 
If you need a library that we have not yet whitelisted, feel free to reach out to us.

The most straightforward way to create and register a labeling function is as follows:

```python
def my_first_lf(record):
    """
    Checks whether a headline contains clickbait-like terms.
    """

    clickbait_terms = [
        'should', 'reasons', 'you', #...
    ]
    headline = record['attributes']['headline'].lower()
    for clickbait_term in clickbait_terms:
        if clickbait_term in headline:
            return 'Clickbait'
    return 'Regular'

lf_first = onetask.build_lf(my_first_lf)

def my_second_lf(record):
    """
    Checks whether a headline starts with two digits.
    """

    import re # standard regular expressions library
    pattern = "^[1-9][0-9]" # two digits at start of string
    headline = record['attributes']['headline'].lower()
    if re.match(pattern, headline):
        return 'Clickbait'

lf_second = onetask.build_lf(my_second_lf)
```

### [](https://github.com/onetask-ai/onetask-python#testing-labeling-functions-locally)Testing Labeling Functions Locally

Before you register your labeling functions, you can run them on your local machine, e.g. to ensure syntactic correctness.

```python
record_hit_list_first = lf_first.execute(record_list) # this runs locally
print(record_hit_list_first)

record_hit_list_second = lf_second.execute(record_list) # this runs locally
print(record_hit_list_second)
```

### [](https://github.com/onetask-ai/onetask-python#registering-labeling-functions)Registering Labeling Functions

If you defined (and optionally tested) your labeling functions, you can register them to your project. 
Once registered, these labeling functions will receive an internal id, which can be used to fetch them back.

```python
client.register_lf(lf_first)
print(lf_first.internal_id)

client.register_lf(lf_second)
print(lf_second.internal_id)
```

### [](https://github.com/onetask-ai/onetask-python#fetching-labeling-functions)Fetching Labeling Functions

You can always fetch your registered labeling functions.

```python
lf_list = client.get_all_lfs()
```

If you have any further questions which are not covered by this README, please do not hesitate to [contact us directly](mailto:info@onetask.ai) 