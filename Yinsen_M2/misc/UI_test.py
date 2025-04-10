from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtCore import Qt, QRectF, QPoint
import sys

class Whiteboard(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        # Set up the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Enable antialiasing
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set up drawing properties
        self.last_point = None
        self.pen = QPen(QColor(0, 0, 0), 2, Qt.PenStyle.SolidLine)
        
        # For panning (dragging the whiteboard)
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        
        # Set up the window
        self.setWindowTitle('Whiteboard')
        self.resize(800, 600)
        
        # Enable drag mode for Shift+Mouse
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        self.initUI()

    def initUI(self):
        """ Add a sample sticky note """
        self.addStickyNote(-100, -100, "Task 1: Research AI Agents")
    
    def addStickyNote(self, x, y, text="New Note"):
        """ Adds a draggable sticky note """
        note = StickyNote(x, y, text)
        self.scene.addItem(note)

    def wheelEvent(self, event):
        """ Zoom in/out on scroll """
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        # Check if Shift key is pressed
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # Start panning
            self.panning = True
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            # Regular drawing mode
            self.last_point = event.pos()
            super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.panning:
            # Calculate how much to pan
            dx = event.x() - self.pan_start_x
            dy = event.y() - self.pan_start_y
            
            # Update pan start position
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()
            
            # Perform the pan
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - dx)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - dy)
        elif self.last_point:
            # Regular drawing mode
            current_point = event.pos()
            line = self.scene.addLine(
                self.last_point.x(), self.last_point.y(),
                current_point.x(), current_point.y(),
                self.pen
            )
            self.last_point = current_point
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.last_point = None
        super().mouseReleaseEvent(event)

class StickyNote(QGraphicsRectItem):
    def __init__(self, x, y, text):
        super().__init__(0, 0, 150, 100)  # Note size
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#FFEB3B")))  # Yellow background
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.textItem = QGraphicsTextItem(text, self)
        self.textItem.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.textItem.setDefaultTextColor(QColor("#000"))
        self.textItem.setPos(10, 10)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    whiteboard = Whiteboard()
    whiteboard.setWindowTitle("AI Workboard")
    whiteboard.resize(800, 600)
    whiteboard.show()
    sys.exit(app.exec())
