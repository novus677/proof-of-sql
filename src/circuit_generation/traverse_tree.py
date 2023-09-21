from common import Comparator, Operator
from common import Node, LiteralNode, ColumnNode, ComparatorNode, OperatorNode, ParenNode
from typing import List

def traverse_tree(node: Node, lines=[]):
    '''
    Traverses the Abstract Syntax Tree (AST) and adds the corresponding lines of Rust code to the lines list.
    This function is called on the root node of the tree.
    '''
    if node is None:
        return
    if not isinstance(node, ParenNode):
        traverse_tree(node.left, lines)
        traverse_tree(node.right, lines)
    else:
        traverse_tree(node.child, lines)
    
    name = "out" if node.counter == -1 else f"val{node.counter}" if isinstance(node, LiteralNode) else f"intermediate{node.counter}"

    if isinstance(node, LiteralNode):
        lines.append(
            f"let {name} = ctx.load_constant(F::from({node.val}));"
        )
    elif isinstance(node, ColumnNode):
        pass
    elif isinstance(node, ComparatorNode):
        if isinstance(node.left, ColumnNode) and isinstance(node.right, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.gate().is_equal(ctx, x, y)).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                # is there a better way to do not equal?
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let is_equal = range.gate().is_equal(ctx, x, y); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.is_less_than(ctx, y, x, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, y, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| range.is_less_than(ctx, x, y, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().zip(db[{node.right.col_index}].iter()).map(|(&x, &y)| {{ \n\t let plus_one = range.gate().add(ctx, y, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        elif isinstance(node.left, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.gate().is_equal(ctx, x, val{node.right.counter})).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let is_equal = range.gate().is_equal(ctx, x, val{node.right.counter}); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.is_less_than(ctx, val{node.right.counter}, x, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, val{node.right.counter}, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| range.is_less_than(ctx, x, val{node.right.counter}, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.left.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, val{node.right.counter}, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        elif isinstance(node.right, ColumnNode):
            if node.comparator == Comparator.EQ:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.gate().is_equal(ctx, val{node.left.counter}, x)).collect();"
                )
            elif node.comparator == Comparator.NEQ:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let is_equal = range.gate().is_equal(ctx, val{node.left.counter}, x); \n\t range.gate().sub(ctx, Constant(F::one()), is_equal) \n }}).collect();"
                )
            elif node.comparator == Comparator.GT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.is_less_than(ctx, x, val{node.left.counter}, 10)).collect();"
                )
            elif node.comparator == Comparator.GTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, val{node.left.counter}, Constant(F::one())); \n\t range.is_less_than(ctx, x, plus_one, 10) \n }}).collect();"
                )
            elif node.comparator == Comparator.LT:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| range.is_less_than(ctx, val{node.left.counter}, x, 10)).collect();"
                )
            elif node.comparator == Comparator.LTE:
                lines.append(
                    f"let {name}: Vec<AssignedValue<F>> = db[{node.right.col_index}].iter().map(|&x| {{ \n\t let plus_one = range.gate().add(ctx, x, Constant(F::one())); \n\t range.is_less_than(ctx, val{node.left.counter}, plus_one, 10) \n }}).collect();"
                )
            else:
                print("Error: invalid comparator")
        else:
            print("Error: at least one side of the comparator must be a column")
    elif isinstance(node, OperatorNode):
        if node.operator == Operator.AND:
            lines.append(
                f"let {name}: Vec<AssignedValue<F>> = intermediate{node.left.counter}.iter().zip(intermediate{node.right.counter}.iter()).map(|(&x, &y)| range.gate().and(ctx, x, y)).collect();"
            )
        elif node.operator == Operator.OR:
            lines.append(
                f"let {name}: Vec<AssignedValue<F>> = intermediate{node.left.counter}.iter().zip(intermediate{node.right.counter}.iter()).map(|(&x, &y)| range.gate().or(ctx, x, y)).collect();"
            )
        else:
            print("Error: invalid operator")
    elif isinstance(node, ParenNode):
        lines.append(f"let {name} = intermediate{node.child.counter};")
    else:
        print("Error: invalid node type")

def gen_lines(root: Node) -> List[str]:
    lines = []
    traverse_tree(root, lines)
    return lines