![kern-python](https://uploads-ssl.webflow.com/61e47fafb12bd56b40022a49/62766400bd3c57b579d289bf_kern-python%20Banner.png)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![pypi 0.0.1](https://img.shields.io/badge/pypi-0.0.1-yellow.svg)](https://pypi.org/project/kern-python-client/0.0.1/)

# Kern AI API for Python

This is the official Python SDK for Kern AI, your IDE for programmatic data enrichment and management.

## Installation

You can set up this library via either running `$ pip install kern-sdk`, or via cloning this repository and running `$ pip install -r requirements.txt` in your repository.

## Usage
Once you installed the package, you can access the application from any Python terminal as follows:

```python
from kern import Client

username = "your-username"
password = "your-password"
project_id = "your-project-id" # can be found in the URL of the web application

client = Client(username, password, project_id)
# if you run the application locally, please the following instead:
# client = Client(username, password, project_id, uri="http://localhost:4455")
```

Now, you can easily fetch the data from your project:
```python
df = client.fetch_export()
```

The `df` contains data of the following scheme:
- all your record attributes are stored as columns, e.g. `headline` or `running_id` if you uploaded records like `{"headline": "some text", "running_id": 1234}`
- per labeling task three columns:
  - `<attribute_name|None>__<labeling_task_name>__MANUAL`: those are the manually set labels of your records
  - `<attribute_name|None>__<labeling_task_name>__WEAK SUPERVISION`: those are the weakly supervised labels of your records
  - `<attribute_name|None>__<labeling_task_name>__WEAK SUPERVISION_confidence`: those are the probabilities or your weakly supervised labels

With the `client`, you easily integrate your data into any kind of system; may it be a custom implementation, an AutoML system or a plain data analytics framework 🚀

## Roadmap
- [ ] Register information sources via wrappers
- [ ] Fetch project statistics


If you want to have something added, feel free to open an [issue](https://github.com/code-kern-ai/kern-python/issues).

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

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
