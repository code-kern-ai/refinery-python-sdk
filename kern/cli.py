from kern import Client
import sys
from wasabi import msg


def pull():
    client = Client.from_secrets_file("secrets.json")
    project_name = client.get_project_details()["name"]
    download_to = f"{project_name}.json"
    client.get_record_export(download_to=download_to)


def help():
    msg.info(
        "With the Kern SDK, you can type commands as `kern <command>`. Currently, we provide the following:"
    )
    msg.info(
        "- kern pull: Download the record export of the project defined in `settings.json` to your local storage."
    )
    msg.info(
        "- kern push <path>: Upload a record file to the project defined in `settings.json` from your local storage. Currently in development."
    )


def main():
    cli_args = sys.argv[1:]
    if len(cli_args) == 0:
        msg.fail(
            "Please provide some arguments when running kern. Type `kern help` for some instructions."
        )
    else:
        command = cli_args[0]
        if command == "pull":
            pull()
        elif command == "push":
            msg.warn("Currently in development.")
        elif command == "help":
            help()
        else:
            msg.fail(
                f"Could not understand command `{command}`. Type `kern help` for some instructions."
            )
