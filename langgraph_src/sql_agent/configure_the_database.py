# download the chinook database from google cloud
import requests

url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"

response = requests.get(url)


if response.status_code == 200:
    # Open a local file in binary write mode
    with open('Chinook.db', 'wb') as file:
        # Write the content of the response to the local file
        file.write(response.content)
    print("file downloaded and saved as Chinook.db")
else:
    print("Error downloading the file,Status code:", response.status_code)


