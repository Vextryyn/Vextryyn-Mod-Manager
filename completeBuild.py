import json
import re
from xml.etree import ElementTree as ET

class CompleteBuild:
    def __init__(self, json_path: str, output_path: str):
        self.json_path = json_path
        self.output_path = output_path

    @staticmethod
    def json_key_to_xml_name(json_key: str) -> str:
        """Converts JSON key names to XML-friendly names (camelCase -> kebab-case)."""
        if json_key.endswith("W"):
            json_key = json_key[:-1]
        xml_name = re.sub(r'([A-Z])', r'-\1', json_key).lower().lstrip('-')
        return xml_name

    def generate_color_xml(self, colors: dict):
        """Generates XML <constantDef> entries from JSON colors."""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>\n<themes>\n']
        for json_key, color_value in colors.items():
            xml_name = self.json_key_to_xml_name(json_key)
            xml_lines.append(f'    <constantDef name="{xml_name}"><color>{color_value}</color></constantDef>\n')
        xml_lines.append('</themes>\n')
        return xml_lines

    def generate_xml(self):
        """Generates an XML file based on the JSON colors, preserving <include> tags if present."""
        with open(self.json_path, "r") as f:
            data = json.load(f)
        colors = data.get("colors", {})

        try:
            # Try to parse the existing output XML (if it exists)
            tree = ET.parse(self.output_path)
            root = tree.getroot()
            # If <themes> has <include> children, preserve them
            includes = root.findall("include")
            if includes:
                xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>\n<themes>\n']
                for include in includes:
                    xml_lines.append(f'    <include filename="{include.attrib["filename"]}"/>\n')
                xml_lines.append('</themes>\n')
            else:
                xml_lines = self.generate_color_xml(colors)
        except (FileNotFoundError, ET.ParseError):
            # No existing file: just generate color XML
            xml_lines = self.generate_color_xml(colors)

        with open(self.output_path, "w") as f:
            f.writelines(xml_lines)

        print(f"XML generated successfully at '{self.output_path}'")
