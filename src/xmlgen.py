class Node:
    """
    Node for a lightweight xml builder.
    """

    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.children = []

    def render(self, indent, offset):
        dest = []
        self._render(indent, offset, dest)
        dest.append('') # causes the trailing newline
        return "\n".join(dest)

    def _render(self, indent, offset, dest):
        """
        Write out the lines for this node to the destination array.
        """
        attrs = []
        for attr in self.attributes:
            attrs.append(f'{attr}="{self.attributes[attr]}"')
        attrs = " ".join(attrs)
        if attrs == "":
            s = ""
        else:
            s = " "
        i = " " * indent
        if len(self.children) == 0:
            dest.append(f"{i}<{self.name}{s}{attrs}/>")
        else:
            dest.append(f"{i}<{self.name}{s}{attrs}>")
            for child in self.children:
                if isinstance(child, str):
                    dest.append(i + child)
                else:
                    child._render(indent + offset, offset, dest)
            dest.append(f"{i}</{self.name}>")

def node(name, attributes = {}, children = []):
    n = Node(name)
    for a in attributes:
        n.attributes[a] = attributes[a]
    for c in children:
        n.children.append(c)
    return n