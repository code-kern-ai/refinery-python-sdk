[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# onetask API for Python - WiP

Official Python SDK for onetask.

## [](https://github.com/onetask-ai/onetask-python#installation)Installation


You can clone the repository and run the setup.py script:

`$ python setup.py install`

## [](https://github.com/onetask-ai/onetask-python#usage)Usage

Before making requests to the API, you need to create an instance of the onetask client. At the moment, you will have to use the org id and the project id:

```python
from onetask import Client
# Instantiate the client using your org_id and project_id
org_id = '<YOUR ORG ID HERE>'
project_id = '<YOUR PROJECT ID HERE>'
client = Client(org_id=org_id, project_id=project_id)
```

You can now register your custom Python function
```python
def my_first_lf(record):
    if "you" in record["headline"].lower():
        return "Clickbait"
client.register_lf(my_first_lf)
```
