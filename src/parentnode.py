from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self, tag, children = [], props = None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("tag cannot be empty")
        if self.children is None:
            raise ValueError("children cannot be empty")
        html_string = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            html_string = f"{html_string}{child.to_html()}"
        return f"{html_string}</{self.tag}>"
