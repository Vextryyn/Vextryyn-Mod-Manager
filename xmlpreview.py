import os
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

class XmlAnimationPreview(QWidget):
    def __init__(self, xml_path, parent=None):
        super().__init__(parent)
        self.xml_path = xml_path
        self.image_map = {}
        self.animations = {}
        self.composed_animations = {}
        self.layer_tints = {
            "reshiram-color": QColor("#1b2526"),
            "zekrom-color": QColor("#070b0b"),
            "reshiram-aura": QColor("#cb4e03"),
            "zekrom-aura": QColor("#00a5c9")
        }
        self.current_animation = None
        self.current_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(200, 200)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.load_xml()
        self.build_composed_animations()
        self.start_first_animation()

    def load_xml(self, xml_path=None):
        if xml_path:
            self.xml_path = xml_path

        tree = ET.parse(self.xml_path)
        self.root = tree.getroot()
        self.image_map.clear()
        self.animations.clear()
        self.composed_xml_nodes = []

        base_dir = os.path.dirname(self.xml_path)

        for img_tag in self.root.findall(".//images"):
            file_path = img_tag.attrib.get("file")
            pixmap = None
            if file_path:
                abs_path = os.path.join(base_dir, file_path)
                pixmap = QPixmap(abs_path)

            for area in img_tag.findall("area"):
                name = area.attrib.get("name")
                tint = area.attrib.get("tint")
                if name and pixmap and not pixmap.isNull():
                    self.image_map[name] = {"pixmap": pixmap, "tint": tint}

        for anim_tag in self.root.findall(".//animation"):
            anim_name = anim_tag.attrib.get("name")
            if not anim_name:
                continue
            frames = []
            for child in anim_tag:
                frames.extend(self.resolve_frames(child))
            if frames:
                self.animations[anim_name] = frames

        for grid_tag in self.root.findall(".//grid"):
            grid_name = grid_tag.attrib.get("name")
            if grid_name:
                self.animations[grid_name] = self.resolve_frames(grid_tag)

        self.composed_xml_nodes = self.root.findall(".//composed")


    def resolve_frames(self, node):
        frames = []

        if node.tag == "frame":
            ref = node.attrib.get("ref")
            file_path = node.attrib.get("file")
            duration = int(node.attrib.get("duration", 50))
            tint = node.attrib.get("tint")

            if file_path:
                abs_path = os.path.join(os.path.dirname(self.xml_path), file_path)
                pixmap = QPixmap(abs_path)
                if not pixmap.isNull():
                    frames.append({
                        "pixmap": pixmap,
                        "duration": duration,
                        "tint": tint
                    })

            elif ref:
                if ref in self.animations:
                    for f in self.animations[ref]:
                        f_copy = f.copy()
                        if tint:
                            f_copy["tint"] = self.layer_tints.get(tint, tint)
                        frames.append(f_copy)
                elif ref in self.image_map:
                    pix_entry = self.image_map[ref]
                    frames.append({
                        "pixmap": pix_entry["pixmap"],
                        "duration": duration,
                        "tint": tint or pix_entry.get("tint")
                    })

        elif node.tag == "grid":
            grid_frames = {}
            for alias in node.findall("alias"):
                ref = alias.attrib.get("ref")
                if not ref or ref == "none":
                    continue
                sub_frames = self.resolve_frames_by_name(ref)
                if sub_frames:
                    grid_frames[ref] = sub_frames
            return [{"grid": grid_frames}]

        elif node.tag == "alias":
            ref = node.attrib.get("ref")
            alias_tint = node.attrib.get("tint")
            sub_frames = self.resolve_frames_by_name(ref)
            for f in sub_frames:
                f_copy = f.copy()
                if alias_tint:
                    f_copy["tint"] = self.layer_tints.get(alias_tint, alias_tint)
                frames.append(f_copy)

        return frames


    def resolve_frames_by_name(self, name):
        if name in self.animations:
            return self.animations[name]

        elif name in self.image_map:
            pix_entry = self.image_map[name]
            return [{"pixmap": pix_entry["pixmap"], "duration": None, "tint": pix_entry.get("tint")}]

        for tag in self.composed_xml_nodes:
            if tag.attrib.get("name") == name:
                frames = []
                for alias_tag in tag.findall("alias"):
                    frames.extend(self.resolve_frames(alias_tag))
                return frames

        for tag in self.root.findall(".//grid"):
            if tag.attrib.get("name") == name:
                grid_layers = {}
                max_length = 0
                for alias_tag in tag.findall("alias"):
                    ref = alias_tag.attrib.get("ref")
                    if ref and ref != "none":
                        sub_frames = self.resolve_frames_by_name(ref)
                        if sub_frames:
                            grid_layers[ref] = sub_frames
                            max_length = max(max_length, len(sub_frames))
                if grid_layers:
                    return [{"grid": grid_layers, "length": max_length}]
                return []


    def build_composed_animations(self):
        self.composed_animations.clear()
        for composed_tag in self.composed_xml_nodes:
            comp_name = composed_tag.attrib.get("name")
            if not comp_name:
                continue
            alias_frames_map = {}
            for alias_tag in composed_tag.findall("alias"):
                alias_name = alias_tag.attrib.get("ref")
                alias_tint = alias_tag.attrib.get("tint")
                frames = self.resolve_frames_by_name(alias_name)
                for f in frames:
                    if alias_tint and alias_tint in self.layer_tints:
                        f["tint"] = self.layer_tints[alias_tint]
                if frames:
                    alias_frames_map[alias_name] = frames
            self.composed_animations[comp_name] = alias_frames_map

    def start_first_animation(self):
        if self.composed_animations:
            first_anim = list(self.composed_animations.keys())[0]
            self.play_animation(first_anim)
        elif self.animations:
            first_anim = list(self.animations.keys())[0]
            self.play_animation(first_anim)

    def play_animation(self, anim_name):
        if anim_name in self.composed_animations:
            self.alias_frames_map = self.composed_animations[anim_name]
            self.current_composed_name = anim_name
        elif anim_name in self.animations:
            self.alias_frames_map = {anim_name: self.animations[anim_name]}
            self.current_composed_name = anim_name
        else:
            print(f"No animation named {anim_name}")
            return

        self.current_index = 0
        self.layer_frame_indices = {alias: 0 for alias in self.alias_frames_map}
        self.display_current_frame()
        self.start_frame_timer()

    def display_current_frame(self):
        if not hasattr(self, "alias_frames_map") or not self.alias_frames_map:
            return

        def all_pixmaps():
            for frames in self.alias_frames_map.values():
                for f in frames:
                    if "pixmap" in f:
                        yield f["pixmap"]
                    elif "grid" in f:
                        for sub_frames in f["grid"].values():
                            for sub_f in sub_frames:
                                if "pixmap" in sub_f:
                                    yield sub_f["pixmap"]

        max_width = max((p.width() for p in all_pixmaps() if p), default=200)
        max_height = max((p.height() for p in all_pixmaps() if p), default=200)

        merged_pixmap = QPixmap(max_width, max_height)
        merged_pixmap.fill(Qt.transparent)
        painter = QPainter(merged_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        log_parts = []

        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue

            idx = self.layer_frame_indices.get(alias_name, 0)
            frame = frames[idx % len(frames)]  

            if "grid" in frame:  
                grid_layers = frame["grid"]
                parent_idx = self.layer_frame_indices.get(alias_name, 0)
                for sub_alias, sub_frames in grid_layers.items():
                    if not sub_frames:
                        continue
                    sub_frame = sub_frames[parent_idx % len(sub_frames)]
                    pix = sub_frame.get("pixmap")
                    frame_tint = sub_frame.get("tint")
                    if isinstance(frame_tint, QColor):
                        final_tint = frame_tint
                    elif isinstance(frame_tint, str):
                        final_tint = QColor(frame_tint) if frame_tint.startswith("#") else self.layer_tints.get(frame_tint)
                    else:
                        final_tint = None

                    if final_tint and pix and not pix.isNull():
                        pix = self.apply_tint(pix, final_tint)

                    if pix and not pix.isNull():
                        painter.drawPixmap(0, 0, pix)

                    log_parts.append(f"{sub_alias}({parent_idx % len(sub_frames)}/{len(sub_frames)-1})")

            else: 
                pix = frame.get("pixmap")
                frame_tint = frame.get("tint")

                if isinstance(frame_tint, QColor):
                    final_tint = frame_tint
                elif isinstance(frame_tint, str):
                    final_tint = QColor(frame_tint) if frame_tint.startswith("#") else self.layer_tints.get(frame_tint)
                else:
                    final_tint = None

                if final_tint and pix and not pix.isNull():
                    pix = self.apply_tint(pix, final_tint)

                if pix and not pix.isNull():
                    painter.drawPixmap(0, 0, pix)

                log_parts.append(f"{alias_name}({idx % len(frames)}/{len(frames)-1})")

        painter.end()

        self.label.setPixmap(
            merged_pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        current_anim_name = getattr(self, "current_composed_name", None)



    def start_frame_timer(self):
        if not hasattr(self, "alias_frames_map") or not self.alias_frames_map:
            return
        durations = []

        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue

            first_frame = frames[0]

            if "grid" in first_frame:
                parent_idx = self.layer_frame_indices.get(alias_name, 0)
                for sub_alias, sub_frames in first_frame["grid"].items():
                    if not sub_frames:
                        continue
                    sub_frame = sub_frames[parent_idx % len(sub_frames)]
                    dur = sub_frame.get("duration")
                    if dur is not None:
                        durations.append(dur)
            elif len(frames) > 1:
                idx = self.layer_frame_indices.get(alias_name, 0)
                dur = frames[idx].get("duration")
                if dur is not None:
                    durations.append(dur)
            else:
                continue

        self.timer.start(min(durations, default=50))

    def update_frame(self):

        if not hasattr(self, "alias_frames_map") or not self.alias_frames_map:
            return

        max_len = 1
        for frames in self.alias_frames_map.values():
            if not frames:
                continue
            first = frames[0]
            if "grid" in first:
                max_len = max(max_len, first.get("length", len(frames)))
            else:
                max_len = max(max_len, len(frames))

        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue
            self.layer_frame_indices[alias_name] = (self.layer_frame_indices.get(alias_name, 0) + 1) % max_len

        self.display_current_frame()

        durations = []
        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue
            first = frames[0]
            if "grid" in first:
                parent_idx = self.layer_frame_indices.get(alias_name, 0)
                for sub_frames in first["grid"].values():
                    if not sub_frames:
                        continue
                    sub_frame = sub_frames[parent_idx % len(sub_frames)]
                    if sub_frame.get("duration"):
                        durations.append(sub_frame["duration"])
            else:
                idx = self.layer_frame_indices.get(alias_name, 0)
                if idx < len(frames) and frames[idx].get("duration"):
                    durations.append(frames[idx]["duration"])

        self.timer.start(min(durations, default=50))


    def set_layer_color(self, layer_name, qcolor):
        if not isinstance(qcolor, QColor):
            qcolor = QColor(qcolor)
        self.layer_tints[layer_name] = QColor(qcolor)
        self.build_composed_animations()
        self.start_first_animation()

    def set_xml_path(self, xml_path):
        self.xml_path = xml_path
        self.timer.stop()
        self.load_xml()
        self.build_composed_animations()
        self.start_first_animation()

    def apply_tint(self, pixmap, qcolor):
        if pixmap.isNull() or not qcolor:
            return pixmap
        color = QColor(qcolor)
        overlay = QPixmap(pixmap.size())
        overlay.fill(color)
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.drawPixmap(0, 0, overlay)
        painter.end()
        return result
