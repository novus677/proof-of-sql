from enum import Enum

import sqlglot

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

# These are the SQL types that we care about (we ignore things like SELECT, TABLE, WHERE, etc.)
sql_types = (
    sqlglot.expressions.EQ,
    sqlglot.expressions.NEQ,
    sqlglot.expressions.GT,
    sqlglot.expressions.GTE,
    sqlglot.expressions.LT,
    sqlglot.expressions.LTE,
    sqlglot.expressions.And,
    sqlglot.expressions.Or,
    sqlglot.expressions.Column,
    sqlglot.expressions.Literal,
    sqlglot.expressions.Paren,
)

class Node:
    '''
    A generic node in the Abstract Syntax Tree (AST).
    In our code, to differentiate Node objects with sqlglot.expressions objects,
    we typically use `node` for a Node object and `sql_node` for a sqlglot.expressions object.
    '''
    def set_counter(self, counter: int):
        self.counter = counter

class LiteralNode(Node):
    '''
    A node that represents a fixed value in the query.
    '''
    def __init__(self, val: int, counter: int, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        self.counter = counter

class ColumnNode(Node):
    '''
    A node that represents a particular column in the query.
    '''
    def __init__(self, col_index: int, counter: int, left=None, right=None):
        self.col_index = col_index
        self.left = left
        self.right = right
        self.counter = counter

class ComparatorNode(Node):
    '''
    A node that represents a comparator in the query.
    '''
    def __init__(self, comparator: Comparator, counter: int, left=None, right=None):
        self.comparator = comparator
        self.left = left
        self.right = right
        self.counter = counter

class OperatorNode(Node):
    '''
    A node that represents an operator in the query.
    '''
    def __init__(self, operator: Operator, counter: int, left=None, right=None):
        self.operator = operator
        self.left = left
        self.right = right
        self.counter = counter

class ParenNode(Node):
    '''
    A node that represents a parenthesis in the query.
    '''
    def __init__(self, counter: int, child=None):
        self.child = child
        self.counter = counter

class NodeSpecification:
    '''
    A class that combines Node objects with their corresponding sqlglot.expressions object.
    '''
    def __init__(self, sql_node, name, custom_node):
        self.sql_node = sql_node
        self.name = name
        self.custom_node = custom_node

    def set_name(self, name):
        self.name = name


def visualize_tree(node: Node, display_counter=False, indent=0):
    '''
    Debugging tool to visualize the Abstract Syntax Tree (AST) defined.
    '''
    ind = "  " * indent
    counter = f", counter={node.counter}" if display_counter else ""
    if isinstance(node, LiteralNode):
        print(f"{ind}({node.val}{counter})")
    elif isinstance(node, ColumnNode):
        print(f"{ind}(col{node.col_index}{counter})")
    elif isinstance(node, ComparatorNode):
        print(f"{ind}({node.comparator.value}{counter})")
        visualize_tree(node.left, display_counter, indent + 2)
        visualize_tree(node.right, display_counter, indent + 2)
    elif isinstance(node, OperatorNode):
        print(f"{ind}({node.operator.value}{counter})")
        visualize_tree(node.left, display_counter, indent + 2)
        visualize_tree(node.right, display_counter, indent + 2)
    elif isinstance(node, ParenNode):
        print(f"{ind}(PAREN{counter})")
        visualize_tree(node.child, display_counter, indent + 2)
    else:
        print("Error: invalid node type")


def backtrack_dfs(sql_node, path, order):
    '''
    Performs a DFS on the AST starting from sql_node and returns the 
    backtracking order. Note that sql_node is not a Node object, but is 
    (usually) a sqlglot.expressions object.
    '''
    if sql_node is None or isinstance(sql_node, sqlglot.expressions.Identifier) or isinstance(sql_node, str):
        return
    path.append(sql_node)

    backtrack_dfs(sql_node.this, path, order)
    backtrack_dfs(sql_node.expression, path, order)

    backtracked_node = path.pop()
    order.append(backtracked_node)


def gen_backtrack_order(sql_node):
    path = []
    order = []
    backtrack_dfs(sql_node, path, order)
    return order


def write_circuit(lines, schema):
    '''
    Writes the lines of Rust code to a file called "generated_circuit.rs".
    '''
    with open("examples/template.txt", "r") as f:
        template = f.readlines()
    
    line_number_circuit = 38 # line number to insert circuit logic
    template[line_number_circuit - 1: line_number_circuit - 1] = ["\t" + line + "\n" for line in lines]

    line_number_parameter = 16 # line number to insert NUM_COLS
    template[line_number_parameter - 1] = f"const NUM_COLS: usize = {schema.num_columns};\n"

    with open("examples/generated_circuit.rs", "w") as f:
        f.writelines(template)