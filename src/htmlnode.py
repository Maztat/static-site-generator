from __future__ import annotations

class HTMLNode():
    def __init__(self, tag: str | None = None, value: str | None = None, children: list[HTMLNode] | None = None, props: dict[str, str] | None = None):
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: list[HTMLNode] | None = children
        self.props: dict[str, str] | None = props
    
    def to_html(self) -> str:
        raise NotImplementedError
    
    def props_to_html(self) -> str:
        html_string = ""
        if self.props:
            for prop in self.props.keys():
                html_string = f"{html_string} {prop}='{self.props[prop]}'"
        return html_string
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
