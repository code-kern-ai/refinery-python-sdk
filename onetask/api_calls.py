# -*- coding: utf-8 -*-
import pkg_resources
from onetask import exceptions, settings
import requests

try:
    version = pkg_resources.get_distribution("onetask").version
except pkg_resources.DistributionNotFound:
    version = "noversion"


# no call to the onetask system, therefore include it here
def create_session_token(user_name: str, password: str):
    headers = {"Accept": "application/json"}
    action_url = (
        requests.get(settings.get_authentication_url(), headers=headers)
        .json()
        .get("ui")
        .get("action")
    )
    session_token = (
        requests.post(
            action_url,
            headers=headers,
            json={
                "method": "password",
                "password": password,
                "password_identifier": user_name,
            },
        )
        .json()
        .get("session_token")
    )

    return session_token


class GraphQLRequest:
    def __init__(self, query, variables, session_token):
        self.query = query
        self.variables = variables
        self.session_token = session_token

    def execute(self):
        body = {
            "query": self.query,
            "variables": self.variables,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"python-sdk-{version}",
            "Authorization": f"Bearer {self.session_token}",
        }

        response = requests.post(url=settings.graphql(), json=body, headers=headers)

        status_code = response.status_code

        json_data = response.json()

        if status_code == 200:
            return json_data
        else:
            error_code = json_data.get("error_code")
            error_message = json_data.get("error_message")
            exception = exceptions.get_api_exception_class(
                status_code=status_code,
                error_code=error_code,
                error_message=error_message,
            )
            raise exception


class ProjectByProjectId(GraphQLRequest):
    def __init__(self, project_id, session_token):
        QUERY = """
        query ($projectId: ID!) {
            projectByProjectId(projectId: $projectId) {
                id
                labels {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        }
        """

        variables = {
            "projectId": project_id,
        }

        super().__init__(QUERY, variables, session_token)
        try:
            self.data = self.execute()
            self.exists = self.data.get("data").get("projectByProjectId") is not None
        except exceptions.APIError:
            self.exists = False


class ManuallyLabeledRecords(GraphQLRequest):
    def __init__(self, project_id, session_token):
        data = ProjectByProjectId(project_id, session_token).data
        edges = data["data"]["projectByProjectId"]["labels"]["edges"]
        manual = [edge["node"]["name"] for edge in edges]

        QUERY = """
        query ($projectId: ID!, $manual: [String!]) {
            searchRecords(projectId: $projectId, manual: $manual) {
                data
                    labelAssociations {
                    edges {
                        node {
                            label {
                                name
                            }
                            source
                        }
                    }
                }
            }
        }

        """

        variables = {"projectId": project_id, "manual": manual}

        super().__init__(QUERY, variables, session_token)
        self.data = self.execute()


class CreateLabelingFunction(GraphQLRequest):
    def __init__(self, project_id, name, function, description, session_token):
        QUERY = """
        mutation (
            $projectId: ID!, 
            $name: String!, 
            $function: String!, 
            $description: String!
        ) {
            createLabelingFunction(
                projectId: $projectId, 
                name: $name, 
                function: 
                $function, 
                description: $description
            ) {
                labelingFunction {
                    id
                }
            }
        }
        """

        variables = {
            "projectId": project_id,
            "name": name,
            "function": function,
            "description": description,
        }

        super().__init__(QUERY, variables, session_token)
        _ = self.execute()
