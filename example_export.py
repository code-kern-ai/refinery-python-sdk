from refinery import Client

client = Client.from_secrets_file("secrets.json")

print("Let's look into project details...")
print(client.get_project_details())

print("-" * 10)
print("And these are the first 10 records...")
print(client.get_record_export().head(10))
