import re
from schema import Schema

class Query:
    def __init__(self, schema: Schema, raw_query: str):
        self.schema = schema
        self.raw_query = raw_query
        self.select_expr = None
        self.from_expr = None # this is the table that we query from, but we don't actually use this
        self.where_expr = None

        # get relevant expressions for the separate components of the query
        try:
            select_expr = re.search(r'SELECT\s+(.*?)\s+FROM', self.raw_query).group(1).strip()
            from_expr = re.search(r'FROM\s+(.*?)(\s+WHERE|\s*$)', self.raw_query).group(1).strip()
            where_match = re.search(r'WHERE\s+(.*)', self.raw_query)
            if where_match:
                where_expr = where_match.group(1).strip()
        except AttributeError as e:
            return f"Invalid SQL query format: {e}"
        
        self.select_expr = select_expr
        self.from_expr = from_expr
        self.where_expr = where_expr

        # get relevant columns from the query
        if self.select_expr == "*":
            self.columns = self.schema.column_names
        else:
            self.columns = self.select_expr.split(',')

        # get relevant column indices from the query
        self.column_indices = [self.schema.column_name_indices[column] for column in self.columns]

    