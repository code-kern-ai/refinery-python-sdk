# -*- coding: utf-8 -*-

from wasabi import msg
import pandas as pd
from kern import authentication, api_calls, settings, exceptions, util
from typing import List, Optional, Dict
import json
import os.path
from tqdm import tqdm
import spacy


class Client:
    """Client object which can be used to directly address the Kern AI API.

    Args:
        user_name (str): Your username for the application.
        password (str): The respective password. Do not share this!
        project_id (str): The link to your project. This can be found in the URL in an active project.
        uri (str, optional): Link to the host of the application. Defaults to "https://app.kern.ai".

    Raises:
        exceptions.get_api_exception_class: If your credentials are incorrect, an exception is raised.
    """

    def __init__(
        self, user_name: str, password: str, project_id: str, uri=settings.DEFAULT_URI
    ):
        settings.set_base_uri(uri)
        self.session_token = authentication.create_session_token(
            user_name=user_name, password=password
        )
        if self.session_token is not None:
            msg.good("Logged in to system.")
        else:
            msg.fail(f"Could not log in at {uri}. Please check username and password.")
            raise exceptions.get_api_exception_class(401)
        self.project_id = project_id

    @classmethod
    def from_secrets_file(cls, path_to_file: str):
        """Creates a Client object from a secrets file.

        Args:
            path_to_file (str): Path to the secrets file.

        Returns:
            Client: kern.Client object.
        """
        with open(path_to_file, "r") as file:
            content = json.load(file)
        uri = content.get("uri")
        if uri is None:
            uri = settings.DEFAULT_URI
        return cls(
            user_name=content["user_name"],
            password=content["password"],
            project_id=content["project_id"],
            uri=uri,
        )

    def get_project_details(self) -> Dict[str, str]:
        """Collect high-level information about your project: name, description, and tokenizer

        Returns:
            Dict[str, str]: dictionary containing the above information
        """
        url = settings.get_project_url(self.project_id)
        api_response = api_calls.get_request(url, self.session_token)
        return api_response

    def get_lookup_list(self, list_id: str) -> Dict[str, str]:
        """Fetches a lookup list of your current project.

        Args:
            list_id (str): The ID of the lookup list.

        Returns:
            Dict[str, str]: Containing the specified lookup list of your project.
        """
        url = settings.get_lookup_list_url(self.project_id, list_id)
        api_response = api_calls.get_request(url, self.session_token)
        return api_response

    def get_lookup_lists(self) -> List[Dict[str, str]]:
        """Fetches all lookup lists of your current project

        Returns:
            List[Dict[str, str]]: Containing the lookups lists of your project.
        """
        lookup_lists = []
        for lookup_list_id in self.get_project_details()["knowledge_base_ids"]:
            lookup_list = self.get_lookup_list(lookup_list_id)
            lookup_lists.append(lookup_list)
        return lookup_lists

    def get_record_export(
        self,
        num_samples: Optional[int] = None,
        download_to: Optional[str] = None,
        tokenize: Optional[bool] = True,
    ) -> pd.DataFrame:
        """Collects the export data of your project (i.e. the same data if you would export in the web app).

        Args:
            num_samples (Optional[int], optional): If set, only the first `num_samples` records are collected. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame containing your record data.
        """
        url = settings.get_export_url(self.project_id)
        api_response = api_calls.get_request(
            url, self.session_token, **{"num_samples": num_samples}
        )
        df = pd.DataFrame(api_response)

        if tokenize:
            tokenize_attributes = []
            for column in df.columns:
                if "__confidence" in column:
                    dtype = type(df[column].iloc[0])
                    if dtype == list:
                        attribute = column.split("__")[0]
                        tokenize_attributes.append(attribute)

            if len(tokenize_attributes) > 0:
                tokenizer_package = self.get_project_details()["tokenizer"]
                if not spacy.util.is_package(tokenizer_package):
                    spacy.cli.download(tokenizer_package)

                nlp = spacy.load(tokenizer_package)

                msg.info(f"Tokenizing data with spaCy '{tokenizer_package}'.")
                msg.info(
                    "This will be provided from the server in future versions of Kern refinery."
                )

                tqdm.pandas(desc="Applying tokenization locally")
                for attribute in tokenize_attributes:
                    df[f"{attribute}__tokenized"] = df[attribute].progress_apply(
                        lambda x: nlp(x)
                    )

            else:
                msg.info("No tokenization necessary.")

        if download_to is not None:
            df.to_json(download_to, orient="records")
            msg.good(f"Downloaded export to {download_to}")
        return df

    def post_file_import(
        self, path: str, import_file_options: Optional[str] = ""
    ) -> bool:
        """Imports a file into your project.

        Args:
            path (str): Path to the file to import.
            import_file_options (Optional[str], optional): Options for the Pandas import. Defaults to None.

        Raises:
            FileImportError: If the file could not be imported, an exception is raised.

        Returns:
            bool: True if the file was imported successfully, False otherwise.
        """
        if not os.path.exists(path):
            raise exceptions.FileImportError(
                f"Given filepath is not valid. Path: {path}"
            )
        last_path_part = path.split("/")[-1]
        file_name = f"{last_path_part}_SCALE"

        FILE_TYPE = "records"
        # config
        config_url = settings.get_base_config(self.project_id)
        config_api_response = api_calls.get_request(
            config_url,
            self.session_token,
        )
        endpoint = config_api_response.get("KERN_S3_ENDPOINT")

        # credentials
        credentials_url = settings.get_import_url(self.project_id)
        credentials_api_response = api_calls.post_request(
            credentials_url,
            {
                "file_name": file_name,
                "file_type": FILE_TYPE,
                "import_file_options": import_file_options,
            },
            self.session_token,
        )
        credentials = credentials_api_response["Credentials"]
        access_key = credentials["AccessKeyId"]
        secret_key = credentials["SecretAccessKey"]
        session_token = credentials["SessionToken"]
        upload_task_id = credentials_api_response["uploadTaskId"]
        bucket = credentials_api_response["bucket"]
        success = util.s3_upload(
            access_key,
            secret_key,
            session_token,
            bucket,
            endpoint,
            upload_task_id,
            path,
            file_name,
        )
        if success:
            msg.good(f"Uploaded {path} to your project.")
            return True
        else:
            msg.fail(f"Could not upload {path} to your project.")
            return False
