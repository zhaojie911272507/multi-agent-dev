from langgraph.prebuilt import create_react_agent
from langgraphsrc.SQLAgent.Toolkit import tools
from langgraphsrc.SQLAgent.initChatModel import llm
from langgraphsrc.SQLAgent.SQLDatabase import db

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
)

# from IPython.display import Image, display
#
# try:
#     # display(Image(graph.get_graph().draw_mermaid_png()))
#     # 获取 PNG 数据
#     png_data = agent.get_graph().draw_mermaid_png()
#     filename = "reactAgent.png"
#     # 保存到本地
#     with open(filename, "wb") as f:
#         f.write(png_data)
#
#     # 显示图像（确保路径正确）
#     display(Image(filename=filename))

# except Exception:
#     # This requires some extra dependencies and is optional
#     pass


question = "哪种类型的音乐平均曲目最长？请使用中文回答。"

for step in agent.stream(
        {"messages":[{"role": "user","content":question}]},
        stream_mode="values",
):
    step["messages"][-1].pretty_print()



'''
================================ Human Message =================================

哪种类型的音乐平均曲目最长？
================================== Ai Message ==================================
Tool Calls:
  sql_db_list_tables (call_0_3a453ffc-8c4d-4cd9-9bb7-91e5ba894d39)
 Call ID: call_0_3a453ffc-8c4d-4cd9-9bb7-91e5ba894d39
  Args:
================================= Tool Message =================================
Name: sql_db_list_tables

Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, Track
================================== Ai Message ==================================
Tool Calls:
  sql_db_schema (call_0_b107882a-9bc6-436e-a554-4c85feabce7d)
 Call ID: call_0_b107882a-9bc6-436e-a554-4c85feabce7d
  Args:
    table_names: Genre, Track
================================= Tool Message =================================
Name: sql_db_schema


CREATE TABLE "Genre" (
	"GenreId" INTEGER NOT NULL, 
	"Name" NVARCHAR(120), 
	PRIMARY KEY ("GenreId")
)

/*
3 rows from Genre table:
GenreId	Name
1	Rock
2	Jazz
3	Metal
*/


CREATE TABLE "Track" (
	"TrackId" INTEGER NOT NULL, 
	"Name" NVARCHAR(200) NOT NULL, 
	"AlbumId" INTEGER, 
	"MediaTypeId" INTEGER NOT NULL, 
	"GenreId" INTEGER, 
	"Composer" NVARCHAR(220), 
	"Milliseconds" INTEGER NOT NULL, 
	"Bytes" INTEGER, 
	"UnitPrice" NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY ("TrackId"), 
	FOREIGN KEY("MediaTypeId") REFERENCES "MediaType" ("MediaTypeId"), 
	FOREIGN KEY("GenreId") REFERENCES "Genre" ("GenreId"), 
	FOREIGN KEY("AlbumId") REFERENCES "Album" ("AlbumId")
)

/*
3 rows from Track table:
TrackId	Name	AlbumId	MediaTypeId	GenreId	Composer	Milliseconds	Bytes	UnitPrice
1	For Those About To Rock (We Salute You)	1	1	1	Angus Young, Malcolm Young, Brian Johnson	343719	11170334	0.99
2	Balls to the Wall	2	2	1	None	342562	5510424	0.99
3	Fast As a Shark	3	2	1	F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman	230619	3990994	0.99
*/
================================== Ai Message ==================================
Tool Calls:
  sql_db_query (call_0_86ee7443-ffe3-4d08-8bb5-5b85dea276d6)
 Call ID: call_0_86ee7443-ffe3-4d08-8bb5-5b85dea276d6
  Args:
    query: SELECT g.Name AS Genre, AVG(t.Milliseconds) / 1000 AS AvgDurationInSeconds FROM Track t JOIN Genre g ON t.GenreId = g.GenreId GROUP BY g.Name ORDER BY AvgDurationInSeconds DESC LIMIT 5;
================================= Tool Message =================================
Name: sql_db_query

[('Sci Fi & Fantasy', 2911.7830384615386), ('Science Fiction', 2625.549076923077), ('Drama', 2575.28378125), ('TV Shows', 2145.041021505376), ('Comedy', 1585.263705882353)]
================================== Ai Message ==================================

The music genres with the longest average track durations are:

1. **Sci Fi & Fantasy**: ~2911.78 seconds (48.53 minutes)
2. **Science Fiction**: ~2625.55 seconds (43.76 minutes)
3. **Drama**: ~2575.28 seconds (42.92 minutes)
4. **TV Shows**: ~2145.04 seconds (35.75 minutes)
5. **Comedy**: ~1585.26 seconds (26.42 minutes)


test2 
================================ Human Message =================================

哪种类型的音乐平均曲目最长？请使用中文回答。
================================== Ai Message ==================================
Tool Calls:
  sql_db_list_tables (call_0_a3d88f35-d69a-4040-867e-766340ad4e8e)
 Call ID: call_0_a3d88f35-d69a-4040-867e-766340ad4e8e
  Args:
================================= Tool Message =================================
Name: sql_db_list_tables

Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, Track
================================== Ai Message ==================================
Tool Calls:
  sql_db_schema (call_0_0acde240-1eb4-43c4-9e29-476fb36f5819)
 Call ID: call_0_0acde240-1eb4-43c4-9e29-476fb36f5819
  Args:
    table_names: Track, Genre
================================= Tool Message =================================
Name: sql_db_schema


CREATE TABLE "Genre" (
	"GenreId" INTEGER NOT NULL, 
	"Name" NVARCHAR(120), 
	PRIMARY KEY ("GenreId")
)

/*
3 rows from Genre table:
GenreId	Name
1	Rock
2	Jazz
3	Metal
*/


CREATE TABLE "Track" (
	"TrackId" INTEGER NOT NULL, 
	"Name" NVARCHAR(200) NOT NULL, 
	"AlbumId" INTEGER, 
	"MediaTypeId" INTEGER NOT NULL, 
	"GenreId" INTEGER, 
	"Composer" NVARCHAR(220), 
	"Milliseconds" INTEGER NOT NULL, 
	"Bytes" INTEGER, 
	"UnitPrice" NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY ("TrackId"), 
	FOREIGN KEY("MediaTypeId") REFERENCES "MediaType" ("MediaTypeId"), 
	FOREIGN KEY("GenreId") REFERENCES "Genre" ("GenreId"), 
	FOREIGN KEY("AlbumId") REFERENCES "Album" ("AlbumId")
)

/*
3 rows from Track table:
TrackId	Name	AlbumId	MediaTypeId	GenreId	Composer	Milliseconds	Bytes	UnitPrice
1	For Those About To Rock (We Salute You)	1	1	1	Angus Young, Malcolm Young, Brian Johnson	343719	11170334	0.99
2	Balls to the Wall	2	2	1	None	342562	5510424	0.99
3	Fast As a Shark	3	2	1	F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman	230619	3990994	0.99
*/
================================== Ai Message ==================================
Tool Calls:
  sql_db_query (call_0_64deba53-99c7-4557-be53-44c8c098883b)
 Call ID: call_0_64deba53-99c7-4557-be53-44c8c098883b
  Args:
    query: SELECT g.Name AS Genre, AVG(t.Milliseconds) / 1000 AS AverageLengthInSeconds FROM Track t JOIN Genre g ON t.GenreId = g.GenreId GROUP BY g.Name ORDER BY AverageLengthInSeconds DESC LIMIT 5;
================================= Tool Message =================================
Name: sql_db_query

[('Sci Fi & Fantasy', 2911.7830384615386), ('Science Fiction', 2625.549076923077), ('Drama', 2575.28378125), ('TV Shows', 2145.041021505376), ('Comedy', 1585.263705882353)]
================================== Ai Message ==================================

平均曲目最长的音乐类型是“科幻与奇幻”（Sci Fi & Fantasy），平均曲目长度约为2911.78秒（约48.53分钟）。



'''


