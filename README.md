[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# onetask API for Python

Official Python SDK for onetask.

## [](https://github.com/onetask-ai/onetask-python#installation)Installation

You can use pip to install the library:

`$ pip install onetask`

You can clone the repository and run the setup.py script:

`$ python setup.py install`

## [](https://github.com/onetask-ai/onetask-python#usage)Usage

The SDK is currently focused solely on labeling functions. You can register your own functions or let our system generate suggestions on which you can build. In the near future, we'll extend the Python SDK to include programmatic imports and exports, data access, and many more.

You begin by creating a `Client` object. The `Client` will generate and store a session token for you based on your user name, password, and project id. The project id can be found in the URL, e.g. https://app.dev.onetask.ai/app/projects/**03f7d82c-f14c-4f0f-a1ff-59533bab30cc**/overview. Simply copy and paste this into the following pattern:

```python
from onetask import Client

username = "your-username"
project_id = "your-project-id"
password = "your-password"
stage="beta" # if you have onetask on local, you can also set stage to "local"
client = Client(username, password, project_id, stage)
```

Once you correctly instantiated your Client, you can start accessing our GraphQL endpoints. Please always ensure that your labeling functions:

return label names that also exist in your project definition
have exactly one parameter; we execute labeling functions on a record-basis
If you need an import statement in your labeling functions, please check if it is given in the [whitelisted libraries](https://onetask.readme.io/reference/whitelisted-libraries). If you need a library that we have not yet whitelisted, feel free to reach out to us.

The most straightforward way to create and register a labeling function is as follows:

```python
def my_labeling_function(record):
  """
  This is my first labeling function. Yay!
  Its purpose is to detect a list of values in the records that tend to
  occur in urgent messages.
  """
  keywords = ["asap", "as soon as possible", "urgent"]
  
  message_lower = record["message"].lower()
  for keyword in keywords:
    if keyword in message_lower:
      return "Urgent"
```

You can then enter them using the client as follows:

```python
client.register_lf(my_labeling_function)
```

And that's it. You should now be able to see your labeling function in the web application. For further steps, please refer to our [readme.io](https://onetask.readme.io/reference/setting-up-the-python-sdk) documentation
