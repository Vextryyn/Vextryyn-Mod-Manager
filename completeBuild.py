import json
import re
import os
from xml.etree import ElementTree as ET

class CompleteBuild:
    def __init__(self, json_path: str, output_path: str, category: str = "colors"):
        self.json_path = json_path
        self.output_path = output_path
        self.category = category

    @staticmethod
    def json_key_to_xml_name(json_key: str) -> str:
        """Convert camelCase JSON keys to kebab-case XML names."""
        if json_key.endswith("W"):
            json_key = json_key[:-1]
        xml_name = re.sub(r'([A-Z])', r'-\1', json_key).lower().lstrip('-')
        return xml_name

    def _read_includes(self):
        """Return list of include filenames if present in existing XML file."""
        includes = []
        if not os.path.exists(self.output_path):
            return includes  # file doesn’t exist — no includes
        try:
            tree = ET.parse(self.output_path)
            root = tree.getroot()
            for inc in root.findall("include"):
                fn = inc.attrib.get("filename")
                if fn:
                    includes.append(fn)
        except ET.ParseError:
            # file exists but not valid XML — treat as no includes
            includes = []
        return includes

    def _generate_constant_defs(self, section_data):
        """Generate <constantDef> lines from JSON data."""
        lines = []
        for json_key, val in section_data.items():
            xml_name = self.json_key_to_xml_name(json_key)
            lines.append(f'    <constantDef name="{xml_name}"><color>{val}</color></constantDef>\n')
        return lines

    def _generate_includes(self, section_data):
        """Generate <include> lines from JSON data (for look/counter)."""
        lines = []
        for _, val in section_data.items():
            # val expected to be "assets/Whatever.xml"
            lines.append(f'    <include filename="{val}"/>\n')
        return lines

    def generate_xml(self):
        # Load JSON config
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        section_data = data.get(self.category, {}) or {}
        if not section_data:
            print(f"[WARN] No data found in category '{self.category}'")
            return

        # Decide output based on category
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>\n', '<themes>\n']

        if self.category == "colors":
            xml_lines.extend(self._generate_constant_defs(section_data))
            print(f"[INFO] Writing constants for '{self.category}' → {self.output_path}")
        else:
            # for look and counter, build <include> entries
            xml_lines.extend(self._generate_includes(section_data))
            print(f"[INFO] Writing includes for '{self.category}' → {self.output_path}")

        xml_lines.append('</themes>\n')

        # Write out file
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.writelines(xml_lines)

        print(f"[SUCCESS] XML written to {self.output_path}")
