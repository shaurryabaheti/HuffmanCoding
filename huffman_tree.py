from queues import Priority_Queue
from nodes import JunctionNode, StringNode, StrictTreeNode, LeafNode, TreeNode

# This function will convert the huffman codes dictionary to a huffman tree
# Return type -> reverseTreeNode
def generate_tree_from_code(code: dict) -> TreeNode:
    
    # Getting a list of all the items in the code
    items = [i for i in code.items()]

    # Creating the top of the huffman tree
    top = TreeNode()
    # Creating children for top (only temporary)

    # Looping over the items
    for item in items:
        # setting the pointer to the top of the tree
        pointer = top
        # looping over the value of the current item
        for index, value in enumerate(item[1]):
            # if we have reached the last character of the value
            if index == len(item[1]) - 1:
                # checking if there is already a node present at the approaching location
                if isinstance(pointer.children[int(value)], LeafNode):
                    # if yes, raise an error
                    raise ValueError # change this
                # Create a leaf node with the value of the current item
                # and setting the respective children of the pointer as the leafnode
                pointer.children[int(value)] = LeafNode(item[0])
            # if it wasn't the end of the value
            else:
                # if the next child to traverse to is None
                if not pointer.children[int(value)]:
                    # create a TreeNode in its place
                    pointer.children[int(value)] = TreeNode()
                # traverse to the respective child node and set the pointer equal to it
                pointer = pointer.children[int(value)]
    
    # Return the final tree
    return top

# This function converts a priority queue to a Junction Tree using the huffman algorithm
# Return type -> JunctionNode
def make_junction_tree(queue: Priority_Queue) -> JunctionNode:
    
    # if the queue is empty, raise an error
    if len(queue) == 0:
        raise ValueError # change this
    # if the queue only has 1 item, return the item itself
    if len(queue) == 1:
        return queue[0]
    
    # else, add the first 2 items to be dequeued to create a junction node
    # and enqueue it back to the priority queue
    value_1 = queue.dequeue()
    value_2 = queue.dequeue()
    queue.enqueue(value_1 + value_2)
    
    # delete the values to save space
    del value_1, value_2
    
    # call the function again passing in the new queue as the argument
    return make_junction_tree(queue=queue)

# This function will convert a JunctionNode tree to a Huffman Tree
# This is done so we dont waste space by storing the integer value inside each junction node
# Which will in turn save memory
# Return type -> TreeNode
def convert_junction_to_tree(node: JunctionNode) -> StrictTreeNode:
    # create a children list and initialise it to None, None at first
    children = [None]*2
    # get the children list of the node
    children_in_node = node.children
    # We need to loop on the numbers 0 and 1 so using range(2)
    for i in range(2):
        # if the current child is StringNode
        if children_in_node[i].type == StringNode:
            # Convert it to a LeafNode and add it to the new children list made
            children[i] = LeafNode(children_in_node[i].value)
        # if it wasn't a string node
        else:
            # Re call the function and add the resultant TreeNode to the new list of children
            children[i] = convert_junction_to_tree(children_in_node[i])
    
    # Return a treenode who's children are the new children created
    return StrictTreeNode(tuple(children))

# This function will convert a huffman tree into huffman codes dictionary
# Return type -> dict [ str : str ]
def get_huffman_codes(node: StrictTreeNode, prev: str='') -> dict [str: str]:
    
    # Create an empty dictionary
    codes = dict()

    # Loop over the children of the node provided
    for i, child in enumerate(node.children):
        # if the current child is a LeafNode, set the code at child value to be 
        # prev concatenated with the index of the current child
        if child.type == LeafNode:
            codes[child.value] = f'{prev}{i}'
        # if not, then call the function again and update the dict with the results
        else:
            codes.update(get_huffman_codes(child, prev=f'{prev}{i}'))
    
    # Return the new formed dictionary
    return codes

# This function will call necessary functions and convert 
# a priority queue directly to huffman codes dictionary
# Return type -> dict [ str : int ]
def generate_code_from_queue(queue: Priority_Queue) -> dict[str: str]:
    # Get the junction tree from the queue
    junction_tree = make_junction_tree(queue)
    # Get the huffman tree from the junction tree
    huffman_tree = convert_junction_to_tree(junction_tree)
    # convert the huffman tree to the huffman codes dictionary
    huffman_codes = get_huffman_codes(huffman_tree)
    # delete the variables that are node needed as they are heavy memory variables
    del huffman_tree, junction_tree
    # return the generated codes
    return huffman_codes