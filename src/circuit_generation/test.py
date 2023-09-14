from query import Query
from schema import Schema

schema = Schema(
    num_columns = 2,
    column_names = ["col1", "col2"]
)

query1 = Query(schema, "SELECT * FROM table1 WHERE col1 = 1")
query2 = Query(schema, "SELECT col2 FROM table1 WHERE col1 = 1")

print(query1['type'])