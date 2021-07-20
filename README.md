[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# onetask API for Python

Official Python SDK for onetask.

## [](https://github.com/onetask-ai/onetask-python#installation)Installation

You can use pip to install the library:

`$ pip install onetask`

You can clone the repository and run the setup.py script:

`$ python setup.py install`

## [](https://github.com/onetask-ai/onetask-python#usage)Usage

Before making requests to the API, you need to create an instance of the onetask client.
To do so, you will have to login like you do in the system while providing the project id you work in:

```python
from onetask import Client
# Instantiate the client using your org_id and project_id
user_name = '<YOUR USER NAME HERE>'
password = '<YOUR PASSWORD HERE>'
project_id = '<YOUR PROJECT ID HERE>'
client = Client(user_name=user_name, password=password, project_id=project_id)
```

You can now register your custom Python function
```python
def my_first_lf(record):
    if "you" in record["headline"].lower():
        return "Clickbait"
client.register_lf(my_first_lf)
```
