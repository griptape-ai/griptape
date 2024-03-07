import xml.etree.ElementTree as ET
import html
from typing import LiteralString


def format_xml(xml_string: LiteralString | str | bytes) -> str:
    root = ET.fromstring(xml_string)
    formatted_lines = []

    def format_element(elem, level=0):
        elem_str = ET.tostring(elem, encoding="unicode", method="xml")
        decoded_elem_str = html.unescape(elem_str)
        formatted_lines.append(decoded_elem_str + "\n")
        for child in elem:
            format_element(child, level + 1)
        if not list(elem):
            formatted_lines.append("\n")

    format_element(root)

    formatted_xml = "".join(formatted_lines)

    return formatted_xml
