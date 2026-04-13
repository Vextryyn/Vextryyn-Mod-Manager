import os
import xml.etree.ElementTree as ET
from collections import OrderedDict

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImageReader, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


class LruPixmapCache:
    def __init__(self, max_items=24):
        self.max_items = max_items
        self._cache = OrderedDict()

    def get(self, key):
        pixmap = self._cache.pop(key, None)
        if pixmap is not None:
            self._cache[key] = pixmap
        return pixmap

    def put(self, key, pixmap):
        if key in self._cache:
            self._cache.pop(key)
        self._cache[key] = pixmap
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)

    def clear(self):
        self._cache.clear()


class XmlAnimationPreview(QWidget):
    def __init__(self, xml_path, parent=None):
        super().__init__(parent)
        self.xml_path = xml_path
        self.root = None

        self.image_defs = {}
        self.animations = {}
        self.composed_animations = {}
        self.composed_defs = {}
        self.grid_defs = {}

        self.layer_tints = {
            "reshiram-color": QColor("#1b2526"),
            "zekrom-color": QColor("#070b0b"),
            "reshiram-aura": QColor("#cb4e03"),
            "zekrom-aura": QColor("#00a5c9"),
        }

        self.current_animation = None
        self.current_index = 0
        self.current_composed_name = None
        self.alias_frames_map = {}
        self.layer_frame_indices = {}
        self.canvas_size = (200, 200)

        # Small bounded cache for decoded source images only.
        self.pixmap_cache = LruPixmapCache(max_items=24)

        # Reused each paint to avoid per-frame full-size QPixmap allocations.
        self._merge_buffer = None
        self._merge_buffer_size = (0, 0)
        self._tint_overlay = None
        self._tint_result = None
        self._tint_buf_size = (0, 0)

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

        self.image_defs.clear()
        self.animations.clear()
        self.composed_animations.clear()
        self.composed_defs.clear()
        self.grid_defs.clear()
        self.alias_frames_map = {}
        self.layer_frame_indices = {}
        self.canvas_size = (200, 200)
        self.pixmap_cache.clear()
        self._merge_buffer = None
        self._merge_buffer_size = (0, 0)
        self._tint_overlay = None
        self._tint_result = None
        self._tint_buf_size = (0, 0)

        base_dir = os.path.dirname(self.xml_path)

        for img_tag in self.root.findall(".//images"):
            file_path = img_tag.attrib.get("file")
            abs_path = os.path.abspath(os.path.join(base_dir, file_path)) if file_path else None

            for area in img_tag.findall("area"):
                name = area.attrib.get("name")
                tint = area.attrib.get("tint")
                if name and abs_path:
                    self.image_defs[name] = {
                        "file": abs_path,
                        "tint": tint,
                    }

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
                self.grid_defs[grid_name] = grid_tag

        for composed_tag in self.root.findall(".//composed"):
            comp_name = composed_tag.attrib.get("name")
            if comp_name:
                self.composed_defs[comp_name] = composed_tag

    def load_pixmap(self, abs_path):
        abs_path = os.path.abspath(abs_path)
        pixmap = self.pixmap_cache.get(abs_path)
        if pixmap is not None:
            return pixmap

        pixmap = QPixmap(abs_path)
        if pixmap.isNull():
            return QPixmap()

        self.pixmap_cache.put(abs_path, pixmap)
        return pixmap

    @staticmethod
    def _image_pixel_size(abs_path):
        """Image dimensions without decoding the full bitmap (saves RAM vs QPixmap)."""
        reader = QImageReader(abs_path)
        if not reader.canRead():
            return 200, 200
        size = reader.size()
        if not size.isValid():
            return 200, 200
        return size.width(), size.height()

    def resolve_frames(self, node):
        frames = []

        if node.tag == "frame":
            ref = node.attrib.get("ref")
            file_path = node.attrib.get("file")
            duration = int(node.attrib.get("duration", 50))
            tint = node.attrib.get("tint")

            if file_path:
                abs_path = os.path.abspath(os.path.join(os.path.dirname(self.xml_path), file_path))
                frames.append({
                    "kind": "image",
                    "file": abs_path,
                    "duration": duration,
                    "tint": tint,
                })

            elif ref:
                if ref in self.animations:
                    for frame in self.animations[ref]:
                        copied = dict(frame)
                        if tint:
                            copied["tint"] = tint
                        if copied.get("duration") is None:
                            copied["duration"] = duration
                        frames.append(copied)

                elif ref in self.image_defs:
                    img = self.image_defs[ref]
                    frames.append({
                        "kind": "image",
                        "file": img["file"],
                        "duration": duration,
                        "tint": tint or img.get("tint"),
                    })

        elif node.tag == "grid":
            grid_frames = {}
            max_length = 1

            for alias in node.findall("alias"):
                ref = alias.attrib.get("ref")
                if not ref or ref == "none":
                    continue

                alias_tint = alias.attrib.get("tint")
                sub_frames = self.resolve_frames_by_name(ref, tint_override=alias_tint)
                if sub_frames:
                    grid_frames[ref] = sub_frames
                    max_length = max(max_length, len(sub_frames))

            if grid_frames:
                return [{
                    "kind": "grid",
                    "grid": grid_frames,
                    "length": max_length,
                }]

        elif node.tag == "alias":
            ref = node.attrib.get("ref")
            alias_tint = node.attrib.get("tint")
            frames.extend(self.resolve_frames_by_name(ref, tint_override=alias_tint))

        return frames

    def resolve_frames_by_name(self, name, tint_override=None):
        if name in self.animations:
            base_frames = self.animations[name]
            if tint_override is None:
                return [dict(frame) for frame in base_frames]

            out = []
            for frame in base_frames:
                copied = dict(frame)
                copied["tint"] = tint_override
                out.append(copied)
            return out

        if name in self.image_defs:
            img = self.image_defs[name]
            return [{
                "kind": "image",
                "file": img["file"],
                "duration": None,
                "tint": tint_override if tint_override is not None else img.get("tint"),
            }]

        if name in self.composed_defs:
            tag = self.composed_defs[name]
            frames = []
            for alias_tag in tag.findall("alias"):
                alias_ref = alias_tag.attrib.get("ref")
                if not alias_ref:
                    continue

                alias_tint = alias_tag.attrib.get("tint")
                effective_tint = tint_override if tint_override is not None else alias_tint
                frames.extend(self.resolve_frames_by_name(alias_ref, tint_override=effective_tint))
            return frames

        if name in self.grid_defs:
            tag = self.grid_defs[name]
            grid_layers = {}
            max_length = 1

            for alias_tag in tag.findall("alias"):
                ref = alias_tag.attrib.get("ref")
                if not ref or ref == "none":
                    continue

                alias_tint = alias_tag.attrib.get("tint")
                effective_tint = tint_override if tint_override is not None else alias_tint
                sub_frames = self.resolve_frames_by_name(ref, tint_override=effective_tint)
                if sub_frames:
                    grid_layers[ref] = sub_frames
                    max_length = max(max_length, len(sub_frames))

            if grid_layers:
                return [{
                    "kind": "grid",
                    "grid": grid_layers,
                    "length": max_length,
                    "tint": tint_override,
                }]

        return []

    def build_composed_animations(self):
        self.composed_animations = {}

        for comp_name, composed_tag in self.composed_defs.items():
            alias_frames_map = {}
            for alias_tag in composed_tag.findall("alias"):
                alias_name = alias_tag.attrib.get("ref")
                alias_tint = alias_tag.attrib.get("tint")
                if not alias_name:
                    continue

                frames = self.resolve_frames_by_name(alias_name, tint_override=alias_tint)
                if frames:
                    alias_frames_map[alias_name] = frames

            self.composed_animations[comp_name] = alias_frames_map

    def start_first_animation(self):
        if self.composed_animations:
            first_anim = next(iter(self.composed_animations))
            self.play_animation(first_anim)
        elif self.animations:
            first_anim = next(iter(self.animations))
            self.play_animation(first_anim)

    def resolve_tint(self, tint_value):
        if isinstance(tint_value, QColor):
            return tint_value

        if isinstance(tint_value, str):
            if tint_value.startswith("#"):
                color = QColor(tint_value)
                return color if color.isValid() else None
            return self.layer_tints.get(tint_value)

        return None

    def frame_pixmap(self, frame):
        if frame.get("kind") != "image":
            return None

        file_path = frame.get("file")
        if not file_path:
            return None

        pixmap = self.load_pixmap(file_path)
        return pixmap if not pixmap.isNull() else None

    def estimate_canvas_size(self, alias_frames_map):
        max_width = 200
        max_height = 200

        for frames in alias_frames_map.values():
            for frame in frames:
                if frame.get("kind") == "image":
                    file_path = frame.get("file")
                    if file_path and os.path.isfile(file_path):
                        w, h = self._image_pixel_size(file_path)
                        max_width = max(max_width, w)
                        max_height = max(max_height, h)

                elif frame.get("kind") == "grid":
                    for sub_frames in frame["grid"].values():
                        for sub_frame in sub_frames:
                            if sub_frame.get("kind") != "image":
                                continue
                            file_path = sub_frame.get("file")
                            if file_path and os.path.isfile(file_path):
                                w, h = self._image_pixel_size(file_path)
                                max_width = max(max_width, w)
                                max_height = max(max_height, h)

        return max_width, max_height

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

        self.current_animation = anim_name
        self.current_index = 0
        self.layer_frame_indices = {alias: 0 for alias in self.alias_frames_map}

        self.pixmap_cache.clear()
        self.canvas_size = self.estimate_canvas_size(self.alias_frames_map)

        self.display_current_frame()
        self.start_frame_timer()

    def apply_tint(self, pixmap, qcolor):
        if pixmap is None or pixmap.isNull() or not qcolor:
            return pixmap

        color = QColor(qcolor)
        if not color.isValid():
            return pixmap

        w, h = pixmap.width(), pixmap.height()
        if self._tint_buf_size != (w, h) or self._tint_overlay is None or self._tint_result is None:
            self._tint_overlay = QPixmap(w, h)
            self._tint_result = QPixmap(w, h)
            self._tint_buf_size = (w, h)

        overlay = self._tint_overlay
        result = self._tint_result
        overlay.fill(color)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.drawPixmap(0, 0, overlay)
        painter.end()

        return result

    def display_current_frame(self):
        if not self.alias_frames_map:
            return

        max_width, max_height = self.canvas_size
        if (
            self._merge_buffer is None
            or self._merge_buffer_size != (max_width, max_height)
        ):
            self._merge_buffer = QPixmap(max_width, max_height)
            self._merge_buffer_size = (max_width, max_height)
        merged_pixmap = self._merge_buffer
        merged_pixmap.fill(Qt.transparent)

        painter = QPainter(merged_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue

            idx = self.layer_frame_indices.get(alias_name, 0)
            frame = frames[idx % len(frames)]

            if frame.get("kind") == "grid":
                parent_idx = self.layer_frame_indices.get(alias_name, 0)

                for sub_frames in frame["grid"].values():
                    if not sub_frames:
                        continue

                    sub_frame = sub_frames[parent_idx % len(sub_frames)]
                    pix = self.frame_pixmap(sub_frame)
                    final_tint = self.resolve_tint(sub_frame.get("tint"))

                    if final_tint and pix and not pix.isNull():
                        pix = self.apply_tint(pix, final_tint)

                    if pix and not pix.isNull():
                        painter.drawPixmap(0, 0, pix)

            else:
                pix = self.frame_pixmap(frame)
                final_tint = self.resolve_tint(frame.get("tint"))

                if final_tint and pix and not pix.isNull():
                    pix = self.apply_tint(pix, final_tint)

                if pix and not pix.isNull():
                    painter.drawPixmap(0, 0, pix)

        painter.end()

        scaled = merged_pixmap.scaled(
            self.label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label.setPixmap(scaled)

    def get_current_frame_duration(self, alias_name, frames):
        if not frames:
            return None

        idx = self.layer_frame_indices.get(alias_name, 0)
        frame = frames[idx % len(frames)]

        if frame.get("kind") == "grid":
            durations = []
            for sub_frames in frame["grid"].values():
                if not sub_frames:
                    continue
                sub_frame = sub_frames[idx % len(sub_frames)]
                dur = sub_frame.get("duration")
                if dur is not None:
                    durations.append(dur)
            return min(durations) if durations else None

        return frame.get("duration")

    def start_frame_timer(self):
        if not self.alias_frames_map:
            return

        durations = []
        for alias_name, frames in self.alias_frames_map.items():
            dur = self.get_current_frame_duration(alias_name, frames)
            if dur is not None:
                durations.append(dur)

        self.timer.start(min(durations, default=50))

    def update_frame(self):
        if not self.alias_frames_map:
            return

        max_len = 1
        for frames in self.alias_frames_map.values():
            if not frames:
                continue

            first = frames[0]
            if first.get("kind") == "grid":
                max_len = max(max_len, first.get("length", len(frames)))
            else:
                max_len = max(max_len, len(frames))

        for alias_name, frames in self.alias_frames_map.items():
            if not frames:
                continue

            self.layer_frame_indices[alias_name] = (
                self.layer_frame_indices.get(alias_name, 0) + 1
            ) % max_len

        self.display_current_frame()

        durations = []
        for alias_name, frames in self.alias_frames_map.items():
            dur = self.get_current_frame_duration(alias_name, frames)
            if dur is not None:
                durations.append(dur)

        self.timer.start(min(durations, default=50))

    def set_layer_color(self, layer_name, qcolor):
        if not isinstance(qcolor, QColor):
            qcolor = QColor(qcolor)

        self.layer_tints[layer_name] = QColor(qcolor)

        if self.current_animation:
            self.display_current_frame()

    def set_xml_path(self, xml_path):
        self.xml_path = xml_path
        self.timer.stop()
        self.load_xml()
        self.build_composed_animations()
        self.start_first_animation()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.alias_frames_map:
            self.display_current_frame()