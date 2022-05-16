from kern import Client
import sys


def pull():
    client = Client.from_secrets_file("secrets.json")
    project_name = client.get_project_details()["name"]
    download_to = f"{project_name}.json"
    client.get_record_export(download_to=download_to)


def main():
    cli_args = sys.argv[1:]

    # currently only need to easily pull data;
    # in the near future, this might be expanded
    cli_arg = cli_args[0]
    if cli_arg == "pull":
        pull()


if __name__ == "__main__":
    main()
