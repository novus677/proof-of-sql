from common import *
from query import Query
from schema import Schema
from traverse_tree import gen_lines

schema = Schema(
    num_columns = 2,
    column_names = ["col1", "col2"]
)

query = Query(schema, "SELECT * FROM table1 WHERE (col1 = col2 OR col1 = 0) AND col2 >= 0 AND col2 < 5")

if __name__ == "__main__":
    col1_1 = ColumnNode(0, 1)
    col2_1 = ColumnNode(1, 2)
    col1_2 = ColumnNode(0, 3)
    literal_1 = LiteralNode(0, 4)
    col2_2 = ColumnNode(1, 5)
    literal_2 = LiteralNode(0, 6)
    col2_3 = ColumnNode(1, 7)
    literal_3 = LiteralNode(5, 8)
    eq_1 = ComparatorNode(Comparator.EQ, 9, col1_1, col2_1)
    eq_2 = ComparatorNode(Comparator.EQ, 10, col1_2, literal_1)
    or_1 = OperatorNode(Operator.OR, 11, eq_1, eq_2)
    paren_1 = ParenNode(12, or_1)
    gte_1 = ComparatorNode(Comparator.GTE, 13, col2_2, literal_2)
    and_1 = OperatorNode(Operator.AND, 14, paren_1, gte_1)
    lt_1 = ComparatorNode(Comparator.LT, 15, col2_3, literal_3)
    and_2 = OperatorNode(Operator.AND, 16, and_1, lt_1)

    # lines1 = gen_lines(and_2)
    # for line in lines1:
    #     print(line)

    # print("----------------------")

    lines2 = query.parse_query(write_file=True)