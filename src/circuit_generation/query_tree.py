import sqlglot
from enum import Enum

query = "SELECT * FROM table1 WHERE (col1 != col2 OR col1 = 0) AND col2 >= 0"
tree = sqlglot.parse_one(query)

class Comparator(Enum):
    EQ = "EQ"
    NEQ = "NEQ"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"

class Operator(Enum):
    AND = "AND"
    OR = "OR"

class Node:
    pass

class LiteralNode(Node):
    def __init__(self, val: int, counter: int, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        self.counter = counter

class ColumnNode(Node):
    def __init__(self, col_index: int, counter: int, left=None, right=None):
        self.col_index = col_index
        self.left = left
        self.right = right
        self.counter = counter

class ComparatorNode(Node):
    def __init__(self, comparator: Comparator, counter: int, left=None, right=None):
        self.comparator = comparator
        self.left = left
        self.right = right
        self.counter = counter

class OperatorNode(Node):
    def __init__(self, operator: Operator, counter: int, left=None, right=None):
        self.operator = operator
        self.left = left
        self.right = right
        self.counter = counter

def traverse_tree(node: Node, lines=[]):
    if node is None:
        return
    traverse_tree(node.left, lines)
    traverse_tree(node.right, lines)
    if isinstance(node, LiteralNode):
        lines.append(
            f"let val{node.counter} = ctx.load_constant(F::from({node.val}));"
        )
    elif isinstance(node, ColumnNode):
        pass
    elif isinstance(node, ComparatorNode):
        if isinstance(node.left, ColumnNode) and isinstance(node.right, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.gate().is_equal(ctx, x, y)).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                # is there a better way to do not equal?
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let is_equal = range.gate().is_equal(ctx, x, y); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.is_less_than(ctx, y, x, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, y, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.is_less_than(ctx, x, y, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let plus_one = range.gate().add(ctx, y, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        elif isinstance(node.left, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.gate().is_equal(ctx, x, val{node.right.counter})).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let is_equal = range.gate().is_equal(ctx, x, val{node.right.counter}); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.is_less_than(ctx, val{node.right.counter}, x, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, val{node.right.counter}, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.is_less_than(ctx, x, val{node.right.counter}, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, val{node.right.counter}, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        elif isinstance(node.right, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.gate().is_equal(ctx, val{node.left.counter}, x)).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let is_equal = range.gate().is_equal(ctx, val{node.left.counter}, x); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.is_less_than(ctx, x, val{node.left.counter}, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, val{node.left.counter}, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.is_less_than(ctx, val{node.left.counter}, x, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let intermediate{node.counter}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, val{node.left.counter}, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        else:
            print("Error: at least one side of the comparator must be a column")
    elif isinstance(node, OperatorNode):
        if node.operator == Operator.AND:
            lines.append(
                f"let intermediate{node.counter}: Vec<AssignedValue<F>> = intermediate{node.left.counter}.iter().zip(intermediate{node.right.counter}.iter()).map(|(&x, &y)| range.gate().and(ctx, x, y)).collect();"
            )
        elif node.operator == Operator.OR:
            lines.append(
                f"let intermediate{node.counter}: Vec<AssignedValue<F>> = intermediate{node.left.counter}.iter().zip(intermediate{node.right.counter}.iter()).map(|(&x, &y)| range.gate().or(ctx, x, y)).collect();"
            )
        else:
            print("Error: invalid operator")


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
    gte_1 = ComparatorNode(Comparator.GTE, 12, col2_2, literal_2)
    and_1 = OperatorNode(Operator.AND, 13, or_1, gte_1)
    lt_1 = ComparatorNode(Comparator.LT, 14, col2_3, literal_3)
    and_2 = OperatorNode(Operator.AND, 15, and_1, lt_1)

    lines = []
    traverse_tree(and_2, lines)

    with open("examples/template.rs", "r") as f:
        template = f.readlines()
    
    line_number = 37
    template[line_number - 1: line_number - 1] = ["\t" + line + "\n" for line in lines]

    with open("examples/generated_circuit.rs", "w") as f:
        f.writelines(template)