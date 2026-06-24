import os, re, shutil

from blocktype import BlockType
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
from textnode import TextNode
from texttype import TextType

def text_node_to_html_node(text_node) -> HTMLNode:
    text_type = text_node.text_type
    match text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"alt": text_node.text, "src": text_node.url})
        case _:
            raise Exception(f"ERROR: Invalid text type {text_type}")

def extract_markdown_images(text: str) -> list[tuple]:
    image_pattern = r"!\[[^\[\]]*\]\([^\(\)]*\)"
    matches = re.findall(image_pattern, text)
    images = []
    for image_str in matches:
        alt_text = ""
        source = ""
        for i in range(2, len(image_str)):
            if image_str[i] == "]":
                if i > 2:
                    alt_text = image_str[2:i]
                image_str = image_str[i + 1:]
                break
        else:
            raise Exception("ERROR: extract_markdown_images(): No matching bracket found for alt text")
        for i in range(1, len(image_str)):
            if image_str[i] == ")":
                if i > 1:
                    source = image_str[1:i]
                break
        else:
            raise Exception("ERROR: extract_markdown_images(): No matching parentheses found for source")
        images.append((alt_text, source))
    return images

def extract_markdown_links(text: str) -> list[tuple]:
    link_pattern = r"(?<!!)\[[^\[\]]*\]\([^\(\)]*\)"
    matches = re.findall(link_pattern, text)
    links = []
    for link_str in matches:
        link_text = ""
        link = ""
        for i in range(1, len(link_str)):
            if link_str[i] == "]":
                if i > 1:
                    link_text = link_str[1:i]
                link_str = link_str[i + 1:]
                break
        else:
            raise Exception("ERROR: extract_markdown_links(): No matching bracket found for link text")
        for i in range(1, len(link_str)):
            if link_str[i] == ")":
                if i > 1:
                    link = link_str[1:i]
                break
        else:
            raise Exception("ERROR: extract_markdown_links(): No matching parentheses found for link")
        links.append((link_text, link))
    return links

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        words = node.text.split(delimiter)
        if len(words) % 2 == 0:
            raise ValueError("unmatched delimiter")
        for i, chunk in enumerate(words):
            if chunk == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(chunk, TextType.TEXT))
            else:
                new_nodes.append(TextNode(chunk, text_type))
    return new_nodes

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        if len(images) == 0:
            if node.text != "":
                new_nodes.append(node)
            continue
        remaining_text = node.text
        for image in images:
            new_node_text = remaining_text.split(f"![{image[0]}]({image[1]})", 1)
            if new_node_text[0] != "":
                new_nodes.append(TextNode(new_node_text[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            remaining_text = new_node_text[1]
        if len(remaining_text) > 0:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            if node.text != "":
                new_nodes.append(node)
            continue
        remaining_text = node.text
        for link in links:
            new_node_text = remaining_text.split(f"[{link[0]}]({link[1]})", 1)
            if new_node_text[0] != "":
                new_nodes.append(TextNode(new_node_text[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            remaining_text = new_node_text[1]
        if len(remaining_text) > 0:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    return new_nodes

def text_to_text_nodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown: str) -> list[str]:
    old_blocks = markdown.split("\n\n")
    blocks = []
    for block in old_blocks:
        block = block.strip()
        if len(block) > 0:
            blocks.append(block)
    return blocks

def block_to_block_type(block: str) -> BlockType:
    if re.match(r"#{1,6} .*", block) is not None:
        return BlockType.HEADING
    if re.match(r"```\n(?:.|\n)*?```$", block) is not None:
        return BlockType.CODE
    lines = block.splitlines()
    for line in lines:
        if line.startswith(">"):
            continue
        break
    else:
        return BlockType.QUOTE
    for line in lines:
        if line.startswith("- "):
            continue
        break
    else:
        return BlockType.UNORDERED_LIST
    count = 1
    for line in lines:
        if line.startswith(f"{count}. "):
            count += 1
            continue
        break
    else:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown: str) -> ParentNode:
    root_node = ParentNode("div", [], None)
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    for block in markdown_to_blocks(markdown):
        root_node.children.append(block_to_html_node(block))
    return root_node

def block_to_html_node(block: str) -> ParentNode:
    match block_to_block_type(block):
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return unordered_list_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return ordered_list_to_html_node(block)
        case _:
            raise Exception(f"ERROR: Invalid BlockType '{block_to_block_type(block)}'")

def paragraph_to_html_node(block: str) -> ParentNode:
    block = " ".join(block.splitlines())
    root_node = ParentNode("p", [], None)
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    for text_node in text_to_text_nodes(block):
        root_node.children.append(text_node_to_html_node(text_node))
    return root_node

def heading_to_html_node(block: str) -> ParentNode:
    header_num = 0
    for char in block:
        if char == " ":
            break
        elif char == "#":
            header_num += 1
        else:
            raise Exception("ERROR: Heading invalid")
    if header_num > 6 or header_num < 1:
        raise Exception(f"ERROR: Invalid number of '#' characters for heading ({header_num})")
    root_node = ParentNode(f"h{header_num}", [], None)
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    block = block.lstrip("#").lstrip()
    for text_node in text_to_text_nodes(block):
        root_node.children.append(text_node_to_html_node(text_node))
    return root_node

def code_to_html_node(block: str) -> ParentNode:
    block = block[4:-3]
    root_node = ParentNode("pre", [ParentNode("code", [LeafNode(None, block)])])
    return root_node

def quote_to_html_node(block: str) -> ParentNode:
    lines = block.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i][1:].strip()
    block = " ".join(lines)
    root_node = ParentNode("blockquote", [])
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    for text_node in text_to_text_nodes(block):
        root_node.children.append(text_node_to_html_node(text_node))
    return root_node

def unordered_list_to_html_node(block: str) -> ParentNode:
    lines = block.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i][2:]
    root_node = ParentNode("ul", [])
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    for line in lines:
        line_node = ParentNode("li", [])
        if line_node.children is None:
            raise Exception("ERROR: root_node.children cannot be None")
        for text_node in text_to_text_nodes(line):
            line_node.children.append(text_node_to_html_node(text_node))
        root_node.children.append(line_node)
    return root_node

def ordered_list_to_html_node(block: str) -> ParentNode:
    lines = block.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i].split(". ", 1)[1]
    root_node = ParentNode("ol", [])
    if root_node.children is None:
        raise Exception("ERROR: root_node.children cannot be None")
    for line in lines:
        line_node = ParentNode("li", [])
        if line_node.children is None:
            raise Exception("ERROR: root_node.children cannot be None")
        for text_node in text_to_text_nodes(line):
            line_node.children.append(text_node_to_html_node(text_node))
        root_node.children.append(line_node)
    return root_node

def copy_paste_subdir(from_path: str, dest_path: str) -> None:
    if not os.path.exists(from_path):
        raise Exception(f"ERROR: '{from_path}' does not exist.")
    for dir in os.listdir(from_path):
        from_dir = os.path.join(from_path, dir)
        dest_dir = os.path.join(dest_path, dir)
        if os.path.isdir(from_dir):
            os.mkdir(dest_dir)
            copy_paste_subdir(from_dir, dest_dir)
        elif os.path.isfile(from_dir):
            shutil.copy(from_dir, dest_dir)

def extract_title(markdown: str) -> str:
    lines = markdown.splitlines()
    for line in lines:
        if line.startswith("# "):
            return line[1:].strip()
    raise Exception("ERROR: No title found")
