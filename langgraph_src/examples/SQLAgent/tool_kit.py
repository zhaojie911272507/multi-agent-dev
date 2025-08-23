from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph_src.SQLAgent.init_chat_model import llm

from langgraph_src.SQLAgent.sql_database import db

toolkit = SQLDatabaseToolkit(db=db,llm=llm)

tools = toolkit.get_tools()
if __name__ == '__main__':

    for tool in tools:
        print(f"{tool.name}: {tool.description}\n")



'''
sql_db_query: Input to this tool is a detailed and correct SQL query, output is a result from the database. If the query is not correct, an error message will be returned. If an error is returned, rewrite the query, check the query, and try again. If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_db_schema to query the correct table fields.

sql_db_schema: Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables. Be sure that the tables actually exist by calling sql_db_list_tables first! Example Input: table1, table2, table3

sql_db_list_tables: Input is an empty string, output is a comma-separated list of tables in the database.

sql_db_query_checker: Use this tool to double check if your query is correct before executing it. Always use this tool before executing a query with sql_db_query!

'''