"""
Succinct ZK Takehome
By Xavier D'Mello
April 24, 2024
"""

import math

# Set to True to print all logs as they are created
DEBUG = True


class Node:
    """Represents a node in the computational graph."""

    def __init__(self, name: str, value: int = None):
        """Creates a new node."""
        self.value = value
        self.constraint = lambda: None
        self.name = name

    def __repr__(self):
        """Print the node's name if object is printed"""
        return f"Node({self.name})"


class Builder:
    """Builds a computational graph with nodes and constraints."""

    def __init__(self):
        """Creates a new builder."""
        self.nodes: [Node] = []
        self.constraints = []  # List of equality constraints
        self.log: [str] = []
        self.n_constants = 0  # for node naming purposes only

    def add_log(self, log_message: str):
        """Adds a log message to the log list and prints it if DEBUG is True."""
        self.log.append(log_message)
        if DEBUG:
            print(log_message)

    def get_node_name(self, value: int = None) -> str:
        """
        Generates a unique name for a node.
        Inspiration: Wanted to make a beautiful debug log without over-engineering.
        Input nodes are set to 'a', 'b', 'c', ...
        Constant nodes are set to their value.
        """
        # If value is input node
        if value is None:
            return chr(ord('a') + len(self.nodes) - self.n_constants)
        else:
            # If value is constant
            self.n_constants += 1
            return str(value)

    def init(self) -> Node:
        """Initializes a new node in the graph."""
        node_name = self.get_node_name()
        node = Node(node_name)
        self.nodes.append(node)
        self.add_log(f"Initialized node: {node}")
        return node

    def constant(self, value: int) -> Node:
        """Creates a constant node with the given value."""
        node_name = self.get_node_name(value)
        node = Node(node_name, value)
        self.nodes.append(node)
        self.add_log(f"Created constant node: {node}")
        return node

    def add(self, a: Node, b: Node) -> Node:
        """Adds two nodes and returns the resulting node."""
        node_name = self.get_node_name()
        node = Node(node_name)
        node.constraint = lambda: a.value + b.value
        self.nodes.append(node)
        self.add_log(f"Added nodes: {a} + {b} = {node}")
        return node

    def mul(self, a: Node, b: Node) -> Node:
        """Multiplies two nodes and returns the resulting node."""
        node_name = self.get_node_name()
        node = Node(node_name)
        node.constraint = lambda: a.value * b.value
        self.nodes.append(node)
        self.add_log(f"Multiplied nodes: {a} * {b} = {node}")
        return node

    def assert_equal(self, a: Node, b: Node):
        """Asserts that two nodes are equal."""
        self.constraints.append(lambda: a.value == b.value)
        self.add_log(f"Asserted equality: {a} == {b}")

    def fill_nodes(self, input_nodes: dict):
        """
        Fills in all the nodes of the graph based on some inputs
        and computes the values of derived/constrained nodes.
        """
        # Fill input nodes
        for node, value in input_nodes.items():
            node.value = value
            self.add_log(f"Set input node: {node} = {value}")

        # The leftover unfilled nodes are computed based on constraints.
        for node in self.nodes:
            if node.value is None:
                node.value = node.constraint()
                self.add_log(f"Computed node: {node} = {node.value}")

    def check_constraints(self) -> bool:
        """
        Given a graph that has `fill_nodes` already called on it
        checks that all the constraints hold.
        """
        satisfied = all(constraint() for constraint in self.constraints)
        self.add_log(f"Constraints satisfied: {satisfied}")
        return satisfied

    def hint(self, hint_func) -> Node:
        """
        An API for hinting values that allows you to perform operations
        like division or computing square roots.
        :param hint_func: arbitrary function
        :return: hint node
        """
        node_name = self.get_node_name()
        node = Node(node_name)
        node.constraint = lambda: hint_func()
        self.nodes.append(node)
        self.add_log(f"Created hint node: {node}")
        return node


# Test cases

def test_example_1(a_input: int):
    """Test case for f(a) = a^2 + a + 5"""
    print(f"\nTesting Example 1: f(a) = a^2 + a + 5, a = {a_input}")
    builder = Builder()
    a = builder.init()
    b = builder.mul(a, a)  # b = a^2
    five = builder.constant(5)
    c = builder.add(b, five)  # c = a^2 + 5
    d = builder.add(c, a)  # d = a^2 + a + 5

    builder.fill_nodes({a: a_input})
    assert builder.check_constraints()
    print(f"Example 1 Passed!")


def test_example_2(a_input: int):
    """
    Test case for f(a) = (a+1) / 8
    a+1 is assumed to be divisible by 8.
    """
    print(f"\nTesting Example 2: f(a) = (a+1) / 8, a = {a_input}")
    builder = Builder()
    a = builder.init()
    b = builder.add(a, builder.constant(1))  # b = a + 1
    c = builder.hint(lambda: b.value // 8)  # Hint computed value of c
    eight = builder.constant(8)
    d = builder.mul(c, eight)  # d = c * 8
    builder.assert_equal(b, d)
    builder.fill_nodes({a: a_input})
    assert builder.check_constraints()
    print(f"Example 2 Passed!")


def test_example_3(a_input: int):
    """
    Test case for f(a) = sqrt(a+7)
    a+7 is assumed to be a perfect square.
    """
    print(f"\nTesting Example 3: f(a) = sqrt(a+7), a = {a_input}")
    builder = Builder()
    a = builder.init()
    seven = builder.constant(7)
    b = builder.add(a, seven)  # b = a + 7
    c = builder.hint(lambda: int(math.sqrt(b.value)))  # Hint computed value of c.
    d = builder.mul(c, c)  # d = c^2
    builder.assert_equal(d, b)

    builder.fill_nodes({a: a_input})
    assert builder.check_constraints()
    print(f"Example 3 Passed!")


def test_example_4(a_input: int, b_input: int):
    """
    Test case for f(a, b) = (a * b) / (a + b)
    a and b are assumed to be non-zero and a + b is assumed to be non-zero and divisible by a * b.
    This test case covers using multiple input nodes and a more complex hint function.
    """
    print(f"\nTesting Example 4: f(a, b) = (a * b) / (a + b), a = {a_input}, b = {b_input}")
    builder = Builder()
    a = builder.init()
    b = builder.init()
    c = builder.mul(a, b)  # c = a * b
    d = builder.add(a, b)  # d = a + b
    e = builder.hint(lambda: c.value // d.value)  # Hint computed value of e
    f = builder.mul(e, d)  # f = e * (a + b)
    builder.assert_equal(f, c)

    builder.fill_nodes({a: a_input, b: b_input})
    assert builder.check_constraints()
    print(f"Example 4 Passed!")


def test_edge_cases():
    """Test cases for edge cases"""
    print("\nTesting Edge Cases")

    # Test case: a = 0
    test_example_1(0)
    # a = 0+1, which is not divisible by 8 for example 2
    try:
        test_example_2(0)
    except AssertionError:
        print("Caught AssertionError for not divisible by 8 in Example 2")
    # a = 0+7, which is non-perfect square for example 3
    try:
        test_example_3(0)
    except AssertionError:
        print("Caught AssertionError for non-perfect square in Example 3")

    # Test case: a = negative value
    test_example_1(-5)
    test_example_2(-9)
    test_example_3(-7)

    # Test case: a = large value
    test_example_1(1000)
    test_example_2(1000000 - 1)  # a+1 = 1000000, big number divisible by 8
    test_example_3(10000000000 - 7)  # a+7 = 10000000000, big number & even number of zeroes = perfect square

    # Test case: a = 0 or b = 0 for example 4
    try:
        test_example_4(0, 5)
    except AssertionError:
        print("Caught AssertionError for a = 0 in Example 4")
    try:
        test_example_4(5, 0)
    except AssertionError:
        print("Caught AssertionError for b = 0 in Example 4")

    # Test case: a + b = 0 for example 4
    try:
        test_example_4(2, -2)
    except AssertionError:
        print("Caught AssertionError for a + b = 0 in Example 4")
    except ZeroDivisionError:
        print("Caught ZeroDivisionError for a + b = 0 in Example 4")

    # Test case: a * b not divisible by a + b for example 4
    try:
        test_example_4(4, 2)
    except AssertionError:
        print("Caught AssertionError for a * b not divisible by a + b in Example 4")

    print("\nAll edge case tests passed!")


if __name__ == "__main__":
    test_example_1(3)
    test_example_2(7)
    test_example_3(2)
    test_example_4(6, 3)
    test_edge_cases()
    print("\nAll tests passed!")
