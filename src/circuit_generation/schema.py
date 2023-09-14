from typing import List

class Schema:
    def __init__(self, num_columns: int, column_names: List[str]):
        self.num_columns = num_columns
        self.column_names = column_names
        self.column_name_indices = {
            column_name: i for i, column_name in enumerate(column_names)
        }