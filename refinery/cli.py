from refinery import Client
import sys
from wasabi import msg


def pull():
    client = Client.from_secrets_file("secrets.json")
    project_name = client.get_project_details()["name"]
    download_to = f"{project_name}.json"
    client.get_record_export(download_to=download_to)


def push(file_path):
    client = Client.from_secrets_file("secrets.json")
    client.post_file_import(file_path)


def help():
    msg.info(
        "With the refinery SDK, you can type commands as `rsdk <command>`. Currently, we provide the following:"
    )
    msg.info(
        "- rsdk pull: Download the record export of the project defined in `settings.json` to your local storage."
    )
    msg.info(
        "- rsdk push <path>: Upload a record file to the project defined in `settings.json` from your local storage."
    )


def main():
    cli_args = sys.argv[1:]
    if len(cli_args) == 0:
        msg.fail(
            "Please provide some arguments when running the `rsdk` command. Type `rsdk help` for some instructions."
        )
    else:
        command = cli_args[0]
        if command == "pull":
            pull()
        elif command == "push":
            if len(cli_args) != 2:
                msg.fail("Please provide a path to a file when running rsdk push.")
            else:
                file_path = cli_args[1]
                push(file_path)
        elif command == "help":
            help()
        else:
            msg.fail(
                f"Could not understand command `{command}`. Type `rsdk help` for some instructions."
            )
