#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Ryan Volz
# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of gr-air-modes, derived from GNU Radio's qtgui
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#

# azimuthal projection widget to plot reception range vs. azimuth

import enum

from PyQt5 import QtCore, QtGui, QtWidgets


class NeedleTypes(enum.Enum):
    NeedleIndicator = enum.auto()
    NeedleFull = enum.auto()
    NeedleMirrored = enum.auto()


class CompassWidget(QtWidgets.QWidget):
    angleChanged = QtCore.pyqtSignal(float)

    QtCore.Q_ENUM(NeedleTypes)

    def __init__(self, parent=None):
        super(CompassWidget, self).__init__(parent)

        # Set parameters
        self._needleType = NeedleTypes.NeedleFull
        self._angle = 0.0
        self._margins = 2
        self._pointText = {
            0: "0",
            45: "45",
            90: "90",
            135: "135",
            180: "180",
            225: "225",
            270: "270",
            315: "315",
        }

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        self.backgroundColor = "default"
        self.needleTipColor = "red"
        self.needleBodyColor = "black"
        self.scaleColor = "black"

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(250, 250)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.backgroundColor == "default":
            painter.fillRect(event.rect(), self.palette().brush(QtGui.QPalette.Window))
        else:
            size = self.size()
            center_x = size.width() / 2
            diameter = size.height()
            brush = QtGui.QBrush(
                QtGui.QColor(self.backgroundColor), QtCore.Qt.SolidPattern
            )
            painter.setBrush(brush)
            painter.setPen(QtGui.QPen(QtGui.QColor(self.scaleColor), 2))
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.drawEllipse(
                int(center_x - diameter / 2 + 1), 1, diameter - 4, diameter - 4
            )

        self.drawMarkings(painter)
        self.drawNeedle(painter)

        painter.end()

    def drawMarkings(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min(
            (self.width() - self._margins) / 120.0,
            (self.height() - self._margins) / 120.0,
        )
        painter.scale(scale, scale)

        font = QtGui.QFont(self.font())
        font.setPixelSize(8)
        metrics = QtGui.QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(QtGui.QPen(QtGui.QColor(self.scaleColor)))
        tickInterval = 5
        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(
                    int(-metrics.width(self._pointText[i]) / 2.0),
                    -52,
                    self._pointText[i],
                )
            else:
                painter.drawLine(0, -45, 0, -50)

            painter.rotate(tickInterval)
            i += tickInterval

        painter.restore()

    def drawNeedle(self, painter):
        painter.save()
        # Set up painter
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min(
            (self.width() - self._margins) / 120.0,
            (self.height() - self._margins) / 120.0,
        )
        painter.scale(scale, scale)
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        # Rotate surface for painting
        intAngle = int(round(self._angle))
        painter.rotate(intAngle)

        # Draw the full black needle first if needed
        if self._needleType == NeedleTypes.NeedleFull:
            needleTailBrush = self.palette().brush(QtGui.QPalette.Shadow)
            needleTailColor = QtGui.QColor(self.needleBodyColor)
            needleTailBrush.setColor(needleTailColor)
            painter.setBrush(needleTailBrush)

            painter.drawPolygon(
                QtGui.QPolygon(
                    [
                        QtCore.QPoint(-6, 0),
                        QtCore.QPoint(0, -45),
                        QtCore.QPoint(6, 0),
                        QtCore.QPoint(0, 45),
                        QtCore.QPoint(-6, 0),
                    ]
                )
            )

        # Now draw the red tip (on top of the black needle)
        needleTipBrush = self.palette().brush(QtGui.QPalette.Highlight)
        needleTipColor = QtGui.QColor(self.needleTipColor)
        needleTipBrush.setColor(needleTipColor)
        painter.setBrush(needleTipBrush)

        # First QPoint is the center bottom apex of the needle
        painter.drawPolygon(
            QtGui.QPolygon(
                [
                    QtCore.QPoint(-3, -24),
                    QtCore.QPoint(0, -45),
                    QtCore.QPoint(3, -23),
                    QtCore.QPoint(0, -30),
                    QtCore.QPoint(-3, -23),
                ]
            )
        )

        if self._needleType == NeedleTypes.NeedleMirrored:
            # Rotate
            # Need to account for the initial rotation to see how much more to rotate it.
            if intAngle == 90 or intAngle == -90 or intAngle == 270:
                mirrorRotation = 180
            else:
                mirrorRotation = 180 - intAngle - intAngle
            painter.rotate(mirrorRotation)

            # Paint shadowed indicator
            needleTipBrush = self.palette().brush(QtGui.QPalette.Highlight)
            needleTipColor = QtCore.Qt.gray
            needleTipBrush.setColor(needleTipColor)
            painter.setBrush(needleTipBrush)

            painter.drawPolygon(
                QtGui.QPolygon(
                    [
                        QtCore.QPoint(-3, -25),
                        QtCore.QPoint(0, -45),
                        QtCore.QPoint(3, -25),
                        QtCore.QPoint(0, -30),
                        QtCore.QPoint(-3, -25),
                    ]
                )
            )

        painter.restore()

    def setColors(
        self,
        backgroundColor="default",
        needleTipColor="red",
        needleBodyColor="black",
        scaleColor="black",
    ):
        self.backgroundColor = backgroundColor
        self.needleTipColor = needleTipColor
        self.needleBodyColor = needleBodyColor
        self.scaleColor = scaleColor

        self.update()

    @QtCore.pyqtProperty(NeedleTypes)
    def needleType(self):
        return self._needleType

    @needleType.setter
    def needleType(self, value):
        self._needleType = value
        self.update()

    @QtCore.pyqtProperty(float)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self.change_angle(value)

    def change_angle(self, angle):
        if angle != self._angle:
            if angle < 0.0:
                angle = 360.0 + angle  # Angle will already be negative

            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QWidget()
    compass = CompassWidget()
    spinBox = QtWidgets.QSpinBox()
    spinBox.setRange(0, 359)
    spinBox.valueChanged.connect(compass.change_angle)
    comboBox = QtWidgets.QComboBox()
    needle_type_map = {v.name: v for v in NeedleTypes}

    def change_needletype(name):
        compass.needleType = needle_type_map[name]

    comboBox.addItems(needle_type_map.keys())
    comboBox.setCurrentIndex(1)
    comboBox.currentTextChanged.connect(change_needletype)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(compass)
    layout.addWidget(spinBox)
    layout.addWidget(comboBox)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec_())
