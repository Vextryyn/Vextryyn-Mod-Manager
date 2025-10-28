import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from functools import partial


class CounterPreview(QWidget):
    """
    CounterPreview (Alpha-aware with color pickers)
    - Up to 3 PNG layers
    - Supports RGBA alpha blending
    - Each layer can have its own semi-transparent tint
    """

    def __init__(self, image_paths=None, parent=None):
        super().__init__(parent)

        # Default 3 layers
        self.layer_paths = [None, None, None]
        self.layer_tints = [QColor(255, 255, 255, 255) for _ in range(3)]

        # Display label
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(50, 50)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        # Optional: initial images
        if image_paths:
            for i, path in enumerate(image_paths):
                self.set_layer_image(i, path)

        self.update_preview()

    # -------------------
    # Layer management
    # -------------------
    def set_layer_image(self, index, path):
        """Set image path for a given layer (0–2)."""
        while len(self.layer_paths) <= index:
            self.layer_paths.append(None)
        self.layer_paths[index] = path
        self.update_preview()

    def set_layer_tint(self, index, color: QColor):
        """Set tint color for a layer and redraw."""
        if 0 <= index < len(self.layer_tints):
            self.layer_tints[index] = color
            self.update_preview()

    # -------------------
    # Preview rendering
    # -------------------
    def update_preview(self):
        final_pix = QPixmap(self.width(), self.height())
        final_pix.fill(Qt.transparent)
        painter = QPainter(final_pix)

        for i, path in enumerate(self.layer_paths):
            if not path or not os.path.exists(path):
                continue

            # Load original image
            layer_pix = QPixmap(path)

            # Determine draw mode:
            # Scale main layers, but keep ball icons at original size
            if i < 7:
                # Scale base/side layers to widget
                layer_pix = layer_pix.scaled(
                    self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                draw_x = (self.width() - layer_pix.width()) // 2
                draw_y = (self.height() - layer_pix.height()) // 2
            else:

                scale_factor = 2.0
                new_width = int(layer_pix.width() * scale_factor)
                new_height = int(layer_pix.height() * scale_factor)
                layer_pix = layer_pix.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                draw_x = 250
                draw_y = 100


            # Create tinted copy to avoid affecting other layers
            tinted_pix = QPixmap(layer_pix.size())
            tinted_pix.fill(Qt.transparent)
            temp_painter = QPainter(tinted_pix)
            temp_painter.drawPixmap(0, 0, layer_pix)

            tint = self.layer_tints[i] if i < len(self.layer_tints) else QColor(255, 255, 255, 255)
            if tint != QColor(255, 255, 255, 255):
                temp_painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
                temp_painter.fillRect(layer_pix.rect(), tint)

            temp_painter.end()

            # Draw tinted layer at computed position
            painter.drawPixmap(draw_x, draw_y, tinted_pix)

        painter.end()
        self.label.setPixmap(final_pix)




    # -------------------
    # Hook color pickers
    # -------------------
    def set_layer_tint_by_name(self, layer_name, color):
        # Map logical names to actual layer indices
        name_to_index = {
            "encounter-counter-main": 0,
            "encounter-counter-sub": 1,
            "encounter-counter-font": 2,
            "encounter-counter-ball": 3,
            "encounter-counter-outline": 4,
            "encounter-counter-min-max": 5,
            "encounter-counter-font-border": 6,
            "window-main":7,
            "window-sub":8,
            "window-accent":9,
            "window-other":10,
            "window-button":11

        }
            # 0: self.mainColor,
            # 1: self.subColor,
            # 2: self.minMaxButtonColor,
            # 3: self.ballColor,
            # 4: self.ballOutline,
            # 5: self.mainColorW,
            # 6: self.subColorW,
            # 7: self.accentColorW,
            # 8: self.OtherColorW,
            # 9: self.ButtonColorW

        if layer_name in name_to_index:
            self.set_layer_tint(name_to_index[layer_name], color)
    # Handle resize
    # -------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()
