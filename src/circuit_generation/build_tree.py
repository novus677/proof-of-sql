from common import Comparator, Operator
from common import Node, LiteralNode, ColumnNode, ComparatorNode, OperatorNode, ParenNode, NodeSpecification
from schema import Schema

import sqlglot

def build_tree(backtrack_order, schema: Schema):
    nodes = {}
    for idx, sql_node in enumerate(backtrack_order):
        if isinstance(sql_node, sqlglot.expressions.Literal):
            name = f"literal_{idx}"
            value = sql_node.this
            custom_node = LiteralNode(value, idx)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.Column):
            name = f"column_{idx}"
            col_index = schema.column_name_indices[str(sql_node.this)]
            custom_node = ColumnNode(col_index, idx)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.Or):
            name = f"or_{idx}"
            custom_node = OperatorNode(Operator.OR, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.And):
            name = f"and_{idx}"
            custom_node = OperatorNode(Operator.AND, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.EQ):
            name = f"eq_{idx}"
            custom_node = ComparatorNode(Comparator.EQ, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.NEQ):
            name = f"neq_{idx}"
            custom_node = ComparatorNode(Comparator.NEQ, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.LT):
            name = f"lt_{idx}"
            custom_node = ComparatorNode(Comparator.LT, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.LTE):
            name = f"lte_{idx}"
            custom_node = ComparatorNode(Comparator.LTE, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.GT):
            name = f"gt_{idx}"
            custom_node = ComparatorNode(Comparator.GT, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.GTE):
            name = f"gte_{idx}"
            custom_node = ComparatorNode(Comparator.GTE, idx, nodes[sql_node.this].custom_node, nodes[sql_node.expression].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        elif isinstance(sql_node, sqlglot.expressions.Paren):
            name = f"paren_{idx}"
            custom_node = ParenNode(idx, nodes[sql_node.this].custom_node)
            specification = NodeSpecification(sql_node, name, custom_node)
            nodes[sql_node] = specification
        else:
            print("Error: invalid node type")

    nodes[backtrack_order[-1]].set_name("out")
    nodes[backtrack_order[-1]].custom_node.set_counter(-1)
    return nodes[backtrack_order[-1]].custom_node