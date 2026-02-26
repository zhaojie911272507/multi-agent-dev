from langchain_community.utilities import SQLDatabase

import os
from dotenv import load_dotenv

load_dotenv()

# db = SQLDatabase.from_uri("sqlite:////Users/zhaojie/Downloads/package/Chinook.db")
db = SQLDatabase.from_uri(os.getenv("DB_URI"))


if __name__ == "__main__":
    print(db.dialect)
    print(db.get_usable_table_names())
    print(f'Sample output: {db.run("SELECT * FROM Artist LIMIT 5;")}')

