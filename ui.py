from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QInputDialog, QLineEdit, QHeaderView, QDialog,
    QFormLayout, QDateEdit, QComboBox, QDialogButtonBox, QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget, QFrame
)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QBrush, QPen,
    QLinearGradient, QPixmap, QPalette, QPainter, QPainterPath)
from PyQt5.QtCore import Qt, QSize, QDate
from datetime import datetime, date
from function import *
import sys
import json
import os

# Assets
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BACKDROP_IMG = os.path.join(BASE_DIR, "assets", "backdrop.png")
EYE_IMG      = os.path.join(BASE_DIR, "assets", "eye.png")
SHP_BTN      = os.path.join(BASE_DIR, "assets", "newshipment.png") 

# Palettes:
ORANGE    = "#f97316"
ORANGE_H  = "#fb923c"
BG_MAIN   = "#f3f4f6"
BG_HEADER = "#111111"
BG_CARD   = "#ffffff"
BG_SEARCH = "#2a2a2a"
PURPLE    = "#6b21a8"
TEXT_WHITE = "#ffffff"
TEXT_GRAY  = "#6b7280"
TEXT_DARK  = "#111827"
BORDER     = "#e5e7eb"

# Other Helpers
PRIORITY_CFG = {
    "Critical": {"bg": "#dc2626", "fg": "#ffffff"},
    "High":     {"bg": "#f97316", "fg": "#ffffff"},
    "Medium":   {"bg": "#facc15", "fg": "#713f12"},
    "Low":      {"bg": "#22c55e", "fg": "#14532d"},
}

_ACT_BTN = """
    QPushButton {
        background-color: #1e293b; color: white;
        padding: 4px 10px; border-radius: 14px;
        font-size: 12px; min-width: 64px; min-height: 26px;
        font-family: 'Segoe UI';
    }
    QPushButton:hover   { background-color: #334155; }
    QPushButton:pressed { background-color: #0f172a; }
"""
_DEL_BTN = """
    QPushButton {
        background-color: transparent; color: #dc2626;
        border: 1px solid #dc2626; border-radius: 13px;
        font-size: 13px; min-width: 26px; min-height: 26px;
    }
    QPushButton:hover { background-color: #dc2626; color: white; }
"""

def _make_badge(text: str, bg: str, fg: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
    lbl.setStyleSheet(
        f"background-color:{bg}; color:{fg}; border-radius:10px; padding:3px 12px;")
    lbl.setFixedHeight(26)
    return lbl

# ─────────────────────────────────────────────
# Dialog
# ─────────────────────────────────────────────

class ShipmentDialog(QDialog):
    """
    Dialog for adding or editing a shipment.
    Captures: Item Code, Deadline, Category.
    """
    CATEGORIES = ["Standard", "Express", "Fragile", "Refrigerated", "Hazmat", "Other"]
 
    def __init__(self, parent=None, shipment: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Shipment Details")
        self.setMinimumWidth(380)
        self._build_ui(shipment)
 
    def _build_ui(self, shipment):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
 
        # ── Item Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g. SHP-20240001")
        if shipment:
            self.code_input.setText(shipment.get("item_code", ""))
        layout.addRow("Item Code:", self.code_input)
 
        # ── Deadline
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setMinimumDate(QDate.currentDate())
        if shipment and shipment.get("deadline"):
            self.date_input.setDate(QDate.fromString(shipment["deadline"], "yyyy-MM-dd"))
        else:
            self.date_input.setDate(QDate.currentDate().addDays(3))
        layout.addRow("Deadline:", self.date_input)
 
        # ── Category
        self.cat_input = QComboBox()
        self.cat_input.addItems(self.CATEGORIES)
        if shipment and shipment.get("category"):
            idx = self.CATEGORIES.index(shipment["category"]) \
                if shipment["category"] in self.CATEGORIES else 0
            self.cat_input.setCurrentIndex(idx)
        layout.addRow("Category:", self.cat_input)
 
        # ── Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
 
        # Style
        self.setStyleSheet("""
            QDialog { background: white; }
            QLabel  { font-size: 14px; color: #333; }
            QLineEdit, QDateEdit, QComboBox {
                border: 1px solid #d9bebe;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #800000;
                color: white;
                border-radius: 10px;
                padding: 6px 18px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #a00000; }
        """)
 
    def _validate_and_accept(self):
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "Validation", "Item Code cannot be empty.")
            return
        self.accept()
 
    def get_values(self):
        return {
            "item_code": self.code_input.text().strip().upper(),
            "deadline":  self.date_input.date().toString("yyyy-MM-dd"),
            "category":  self.cat_input.currentText(),
        }

# ─────────────────────────────────────────────
#  Helper: priority badge widget
# ─────────────────────────────────────────────
 
def make_priority_badge(priority: str) -> QWidget:
    badge = QLabel(priority)
    badge.setAlignment(Qt.AlignCenter)
    bg    = PRIORITY_COLORS.get(priority, "#888")
    fg    = PRIORITY_TEXT_COLORS.get(priority, "white")
    badge.setStyleSheet(f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: 10px;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 12px;
            font-family: Helvetica;
        }}
    """)
    container = QWidget()
    container.setStyleSheet("background-color: #fcecec;")
    lay = QHBoxLayout(container)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setAlignment(Qt.AlignCenter)
    lay.addWidget(badge)
    return container

# ─────────────────────────────────────────────
#  Main Window
# ─────────────────────────────────────────────
 
# Window Background
class BackdropWidget(QWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(BACKDROP_IMG)
 
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
 
        # Calling background image
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (scaled.width()  - self.width())  // 2
            y = (scaled.height() - self.height()) // 2
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
 
        # Dark Gradient Overlay
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0,  QColor(0, 0, 0, 200))
        grad.setColorAt(0.5,  QColor(0, 0, 0, 100))
        grad.setColorAt(1.0,  QColor(0, 0, 0,  60))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawRect(self.rect())
 
        # Navigation Bar Tint
        p.setBrush(QBrush(QColor(0, 0, 0, 80)))
        p.drawRect(0, 0, self.width(), 72)
        p.end()
 
# Button Widget (Hover Effects included) 
class PillButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setMinimumWidth(220)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE};
                color: white;
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: 700;
                font-family: 'Segoe UI';
                padding: 0 28px;
            }}
            QPushButton:hover  {{ background-color: {ORANGE_H}; }}
            QPushButton:pressed {{ background-color: #c85c0a; }}
        """)
 
 
# Placeholder for logo and brand
class NavBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(12)
 
        # Logo icon (eye.png)
        eye_pix = QPixmap("assets/eye.png")
        logo_icon = QLabel()
        if not eye_pix.isNull():
            logo_icon.setPixmap(
                eye_pix.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            # Fallback orange square
            logo_icon.setFixedSize(44, 44)
            logo_icon.setStyleSheet(
                f"background:{ORANGE}; border-radius:8px;"
            )
        layout.addWidget(logo_icon, alignment=Qt.AlignVCenter)
 
        brand = QLabel("SWIFT ROUTE")
        brand.setFont(QFont("Segoe UI", 13, QFont.Bold))
        brand.setStyleSheet("color: white; letter-spacing: 2px; background: transparent;")
        layout.addWidget(brand, alignment=Qt.AlignVCenter)
 
        layout.addStretch()
 
 
# Text Content
class TextContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # Big headline
        self.headline = QLabel("Top-notch\nlogistic services")
        self.headline.setFont(QFont("Segoe UI", 48, QFont.Bold))
        self.headline.setStyleSheet(f"color: {ORANGE}; background: transparent; line-height: 1.1;")
        self.headline.setWordWrap(False)
        layout.addWidget(self.headline)
        layout.addSpacing(18)
 
        # Sub-text
        self.sub = QLabel(
            "We take pride in delivering shipments\n"
            "expressively to the comfort of your\nhomes."
        )
        self.sub.setFont(QFont("Segoe UI", 13))
        self.sub.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent;")
        layout.addWidget(self.sub)
 
 
# Action Buttons
class ActionButtons(QWidget):
    def __init__(self, on_manage, on_history, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)
 
        self.buttons = []

        mng_btn = PillButton("Manage Shipments")
        mng_btn.clicked.connect(on_manage)
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(24)
        shadow1.setOffset(0, 4)
        shadow1.setColor(QColor(249, 115, 22, 140))
        mng_btn.setGraphicsEffect(shadow1)
        self.buttons.append(mng_btn)
        layout.addWidget(mng_btn, alignment=Qt.AlignCenter)

        history_btn = PillButton("Shipment History")
        history_btn.clicked.connect(on_history) 
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(24)
        shadow2.setOffset(0, 4)
        shadow2.setColor(QColor(249, 115, 22, 140))
        history_btn.setGraphicsEffect(shadow2)
        self.buttons.append(history_btn)
        layout.addWidget(history_btn, alignment=Qt.AlignCenter)
        
# Welcome Page
class WelcomePage(QWidget):
    def __init__(self, on_manage, on_history, parent=None):
        super().__init__(parent)
 
        self._backdrop = BackdropWidget(self)
 
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
 
        root.addWidget(NavBar())
 
        hero_row = QHBoxLayout()
        hero_row.setContentsMargins(48, 0, 48, 0)
        hero_row.setSpacing(32)
 
        self.text_content = TextContent()
        hero_row.addWidget(self.text_content, stretch=3)
 
        # Pass the navigation callbacks into ActionButtons
        self.action_buttons = ActionButtons(on_manage, on_history)
        hero_row.addWidget(self.action_buttons, stretch=2)
 
        hero_container = QWidget()
        hero_container.setAttribute(Qt.WA_TranslucentBackground)
        hero_container.setLayout(hero_row)
        hero_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 
        root.addWidget(hero_container, stretch=1)
 
    def resizeEvent(self, event):
        self._backdrop.setGeometry(0, 0, self.width(), self.height())
        scale = self.width() / 1140.0
        self.text_content.headline.setFont(
            QFont("Segoe UI", max(12, int(48 * scale)), QFont.Bold))
        self.text_content.sub.setFont(
            QFont("Segoe UI", max(6, int(13 * scale))))
        for btn in self.action_buttons.buttons:
            btn_h  = max(24, int(48 * scale))
            btn_w  = max(110, int(220 * scale))
            radius = btn_h // 2
            btn.setFixedHeight(btn_h)
            btn.setMinimumWidth(btn_w)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ORANGE}; color: white;
                    border: none; border-radius: {radius}px;
                    font-size: {max(7, int(14 * scale))}px;
                    font-weight: 700; font-family: 'Segoe UI';
                    padding: 0 {max(14, int(28 * scale))}px;
                }}
                QPushButton:hover   {{ background-color: {ORANGE_H}; }}
                QPushButton:pressed {{ background-color: #c85c0a; }}
            """)
        super().resizeEvent(event)

# Main Window
class MainWindow(QWidget):
    PAGE_HOME      = 0
    PAGE_SHIPMENTS = 1
    PAGE_HISTORY   = 2
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Swift Route Logistics")
        self.setWindowIcon(QIcon("assets/van.png"))
        self.setMinimumSize(1140, 580)
        self.resize(1140, 580)
 
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
 
        # QStackedWidget — one child visible at a time
        self.stack = QStackedWidget()
        root.addWidget(self.stack)
 
        # Index 0 — Home / hero
        self.welcome_page = WelcomePage(
            on_manage=self.go_to_shipments,
            on_history=self.go_to_history,
        )
        self.stack.addWidget(self.welcome_page)
 
        # Index 1 — Shipment Manager
        self.shipment_page = ShipmentDashboard(
            on_back=self.go_home,
            on_history=self.go_to_history,
            parent=self,
        )
        self.stack.addWidget(self.shipment_page)
 
        # Index 2 — View History
        self.history_page = ViewHistory(self)
        self.stack.addWidget(self.history_page)
 
        self.stack.setCurrentIndex(self.PAGE_HOME)
 
    # ── Navigation ────────────────────────────────────────────────────────
    def go_home(self):
        self.stack.setCurrentIndex(self.PAGE_HOME)
 
    def go_to_shipments(self):
        self.stack.setCurrentIndex(self.PAGE_SHIPMENTS)
 
    def go_to_history(self):
        self.stack.setCurrentIndex(self.PAGE_HISTORY)

# ─────────────────────────────────────────────
#  Shipment Manager Panel
# ─────────────────────────────────────────────

# Dashboard header
class DashBar(QWidget):
    def __init__(self, on_new_shipment, title, show_history_btn=False, on_history=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(16)

        # ── Left: logo + title + date ─────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        eye_pix = QPixmap(EYE_IMG)
        logo = QLabel()
        if not eye_pix.isNull():
            logo.setPixmap(
                eye_pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setFixedSize(36, 36)
            logo.setStyleSheet(f"background:{ORANGE}; border-radius:6px;")
        title_row.addWidget(logo, alignment=Qt.AlignVCenter)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT_WHITE}; background: transparent;")
        title_row.addWidget(title_lbl, alignment=Qt.AlignVCenter)
        left.addLayout(title_row)

        today_str = QDate.currentDate().toString("dddd - MMMM d, yyyy")
        date_lbl = QLabel(today_str)
        date_lbl.setFont(QFont("Segoe UI", 10))
        date_lbl.setStyleSheet(f"color: rgba(255,255,255,0.55); background: transparent;")
        left.addWidget(date_lbl)

        layout.addLayout(left)

        # ── Right: search + button ────────────────────────────────────────
        right = QHBoxLayout()
        right.setSpacing(12)
        right.setAlignment(Qt.AlignVCenter)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search item code")
        self.search.setFixedHeight(40)
        self.search.setMinimumWidth(220)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_SEARCH};
                color: {TEXT_WHITE};
                border: none;
                border-radius: 20px;
                padding: 0 16px;
                font-size: 13px;
                font-family: 'Segoe UI';
            }}
            QLineEdit::placeholder {{ color: rgba(255,255,255,0.4); }}
        """)
        right.addWidget(self.search)

        new_btn = QPushButton("New Shipment")
        new_btn.setFixedHeight(40)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Segoe UI';
                padding: 0 20px;
            }}
            QPushButton:hover   {{ background-color: {ORANGE_H}; }}
            QPushButton:pressed {{ background-color: #c85c0a; }}
        """)
        new_btn.clicked.connect(on_new_shipment)
        right.addWidget(new_btn)

        if show_history_btn and on_history:
            hist_btn = QPushButton("View History")
            hist_btn.setFixedHeight(40)
            hist_btn.setCursor(Qt.PointingHandCursor)
            hist_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255,255,255,0.12);
                    color: white;
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 20px;
                    font-size: 13px;
                    font-family: 'Segoe UI';
                    padding: 0 16px;
                }}
                QPushButton:hover {{ background-color: rgba(255,255,255,0.22); }}
            """)
            hist_btn.clicked.connect(on_history)
            right.addWidget(hist_btn)

        layout.addStretch()
        layout.addLayout(right)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        p.fillPath(path, QColor(BG_HEADER))
        p.end()

# Dashboard Stat     
class DashStat(QWidget):
    def __init__(self, label: str, value, accent: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            QWidget {{
                background-color:{BG_CARD}; border-radius:14px;
                border-left:5px solid {accent};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 12, 20, 12)
        lay.setSpacing(4)

        self._val_lbl = QLabel(str(value))
        self._val_lbl.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self._val_lbl.setStyleSheet(
            f"color:{TEXT_DARK}; background:transparent; border:none;")
        lay.addWidget(self._val_lbl)

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color:{TEXT_GRAY}; background:transparent; border:none;")
        lay.addWidget(lbl)

    def set_value(self, v):
        self._val_lbl.setText(str(v))
 
class ShipmentTable(QWidget):
    COLS = ["Priority", "Item Code", "Deadline", "Days Left",
            "Category", "Options"]

    def __init__(self, shipments: list,
                 on_deliver, on_return, on_edit, on_delete,
                 parent=None):
        super().__init__(parent)
        self._on_deliver = on_deliver
        self._on_return  = on_return
        self._on_edit    = on_edit
        self._on_delete  = on_delete
        self.all_shipments = list(shipments)

        self.setStyleSheet(f"background-color:{BG_CARD}; border-radius:16px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Title + legend
        hdr_row = QHBoxLayout()
        t_lbl = QLabel(f"Active Shipments: {len(shipments)}")
        t_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        t_lbl.setStyleSheet(f"color:{TEXT_DARK}; background:transparent;")
        hdr_row.addWidget(t_lbl)
        hdr_row.addStretch()
        
        layout.addLayout(hdr_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color:{BORDER};")
        layout.addWidget(line)

        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color:transparent; border:none;
                font-size:13px; font-family:'Segoe UI';
                gridline-color:{BORDER};
            }}
            QHeaderView::section {{
                background-color:{BG_MAIN}; color:{TEXT_GRAY};
                font-weight:bold; padding:10px 8px; border:none;
                font-size:12px; font-family:'Segoe UI';
            }}
            QTableWidget::item {{
                padding:6px 8px; border-bottom:1px solid {BORDER};
                
            }}
            QTableWidget::item:selected {{
                background-color:rgba(249,115,22,0.12); color:{TEXT_DARK};
            }}
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setFixedHeight(44)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.Stretch)

        layout.addWidget(self.table)

        self.count_lbl = QLabel()
        self.count_lbl.setFont(QFont("Segoe UI", 10))
        self.count_lbl.setStyleSheet(
            f"color:{TEXT_GRAY}; background:transparent;")
        layout.addWidget(self.count_lbl)

        self.refresh(shipments)

    # table rendering

    def refresh(self, shipments: list):
        self.all_shipments = list(shipments)
        for s in self.all_shipments:
            s["days_remaining"] = compute_days_remaining(s["deadline"])
        sorted_s = brute_force_sort(self.all_shipments)
        self.table.setRowCount(0)
        for s in sorted_s:
            self._add_row(s)

    def filter(self, query: str):
        q = query.strip().lower()
        if not q:
            self.refresh(self.all_shipments)
            return
        filtered = [s for s in self.all_shipments
                    if q in s["item_code"].lower()
                    or q in s.get("category", "").lower()]
        for s in filtered:
            s["days_remaining"] = compute_days_remaining(s["deadline"])
        sorted_f = brute_force_sort(filtered)
        self.table.setRowCount(0)
        for s in sorted_f:
            self._add_row(s)

    # table row rendering

    def _add_row(self, s: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 60)

        days     = s["days_remaining"]
        priority = get_priority(days)
        days_str = (f"{abs(days)}d overdue" if days < 0
                    else "Today" if days == 0
                    else f"{days}d left")

        def cell(text, align=Qt.AlignCenter):
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(align)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        priority_item = cell(priority)
        priority_item.setForeground(
            QColor(PRIORITY_COLORS.get(priority, TEXT_DARK)))
        self.table.setItem(row, 0, priority_item)
        self.table.setItem(row, 1,
            cell(s["item_code"], Qt.AlignCenter))
        self.table.setItem(row, 2, cell(s["deadline"]))

        days_item = cell(days_str)
        days_item.setForeground(
            QColor(PRIORITY_COLORS.get(priority, TEXT_DARK)))
        self.table.setItem(row, 3, days_item)

        self.table.setItem(row, 4, cell(s.get("category", "Standard")))

        # Options cell
        opt = QWidget()
        opt.setStyleSheet("background:transparent;")
        ol = QHBoxLayout(opt)
        ol.setContentsMargins(4, 4, 4, 4)
        ol.setSpacing(6)
        ol.setAlignment(Qt.AlignCenter)

        deliver_btn = QPushButton("Deliver")
        deliver_btn.setStyleSheet(_ACT_BTN)
        deliver_btn.clicked.connect(
            lambda _, sid=s["id"]: self._on_deliver(sid))

        return_btn = QPushButton("Return")
        return_btn.setStyleSheet(_ACT_BTN)
        return_btn.clicked.connect(
            lambda _, sid=s["id"]: self._on_return(sid))

        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(_ACT_BTN)
        edit_btn.clicked.connect(
            lambda _, sid=s["id"]: self._on_edit(sid))

        del_btn = QPushButton("✕")
        del_btn.setStyleSheet(_DEL_BTN)
        del_btn.clicked.connect(
            lambda _, sid=s["id"]: self._on_delete(sid))

        for b in [deliver_btn, return_btn, edit_btn, del_btn]:
            ol.addWidget(b)
        self.table.setCellWidget(row, 5, opt)

# Shipment Dashboard
class ShipmentDashboard(QWidget):
    def __init__(self, on_back=None, on_history=None, parent=None):
        super().__init__(parent)
        self.on_back    = on_back
        self.on_history = on_history
        self.shipments: list = load_json(SHIPMENTS_FILE, [])
        self.setStyleSheet(f"background-color:{BG_MAIN};")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.header = DashBar(
            title="Your Dashboard",
            on_new_shipment=self._add_shipment,
            show_history_btn=True,
            on_history=self.on_history,
        )
        self.header.search.textChanged.connect(self._on_search)
        root.addWidget(self.header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.card_total    = DashStat("Total Shipments", 0, ORANGE)
        self.card_delivered = DashStat("Delivered",      0, "#22c55e")
        self.card_pending   = DashStat("Pending",        0, ORANGE)
        self.card_overdue  = DashStat("Overdue",         0, PURPLE)
        for c in [self.card_total, self.card_delivered,
                  self.card_pending, self.card_overdue]:
            stats_row.addWidget(c)
        root.addLayout(stats_row)

        self.ship_table = ShipmentTable(
            shipments=self.shipments,
            on_deliver=lambda sid: self._confirm_action(sid, "Delivered"),
            on_return =lambda sid: self._confirm_action(sid, "Returned"),
            on_edit   =self._edit_shipment,
            on_delete =self._delete_shipment,
        )
        root.addWidget(self.ship_table, stretch=1)

        if on_back:
            footer = QHBoxLayout()
            back_btn = QPushButton("Back to Home")
            back_btn.setFixedHeight(20)
            back_btn.setCursor(Qt.PointingHandCursor)
            back_btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent; color:{TEXT_GRAY};
                    border:1px solid {BORDER}; border-radius:18px;
                    font-size:12px; font-family:'Segoe UI'; padding:0 18px;
                }}
                QPushButton:hover {{ border-color:{ORANGE}; color:{ORANGE}; }}
            """)
            back_btn.clicked.connect(on_back)
            footer.addStretch()
            footer.addWidget(back_btn)
            root.addLayout(footer)

        self._refresh()

    def _refresh(self):
        self.ship_table.refresh(self.shipments)
        self._update_stats()

    def _update_stats(self):
        s = self.shipments
        total    = len(s)
        pending  = len(s)  # All active shipments are pending
        overdue  = sum(1 for x in s
                       if compute_days_remaining(x["deadline"]) < 0)
        # Count delivered from history
        history = load_json(HISTORY_FILE, [])
        delivered = sum(1 for x in history
                        if x.get("action") == "Delivered")
        self.card_total.set_value(total)
        self.card_delivered.set_value(delivered)
        self.card_pending.set_value(pending)
        self.card_overdue.set_value(overdue)

    def _on_search(self, text: str):
        self.ship_table.filter(text)

    # CRUD Actions
    """ All functionalities here are used in the shipment table."""

    def _add_shipment(self):
        dlg = ShipmentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            vals   = dlg.get_values()
            new_id = max((s["id"] for s in self.shipments), default=0) + 1
            self.shipments.append({
                "id":        new_id,
                "item_code": vals["item_code"],
                "deadline":  vals["deadline"],
                "category":  vals["category"],
                "added_at":  datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            })
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh()

    def _edit_shipment(self, sid: int):
        s = next((x for x in self.shipments if x["id"] == sid), None)
        if not s:
            return
        dlg = ShipmentDialog(self, s)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.get_values()
            s["item_code"] = vals["item_code"]
            s["deadline"]  = vals["deadline"]
            s["category"]  = vals["category"]
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh()

    def _delete_shipment(self, sid: int):
        s = next((x for x in self.shipments if x["id"] == sid), None)
        if not s:
            return
        r = QMessageBox.question(
            self, "Delete Shipment",
            f"Remove shipment '{s['item_code']}'?",
            QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            self.shipments = [x for x in self.shipments if x["id"] != sid]
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh()

    def _confirm_action(self, sid: int, action: str):
        s = next((x for x in self.shipments if x["id"] == sid), None)
        if not s:
            return
        r = QMessageBox.question(
            self, "Confirm",
            f"Mark '{s['item_code']}' as {action}?",
            QMessageBox.Ok | QMessageBox.Cancel)
        if r == QMessageBox.Ok:
            self._move_to_history(s, action)
            self.shipments = [x for x in self.shipments if x["id"] != sid]
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh()

    def _move_to_history(self, s: dict, action: str):
        history = load_json(HISTORY_FILE, [])
        history.append({
            "item_code": s["item_code"],
            "deadline":  s["deadline"],
            "category":  s.get("category", ""),
            "date_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "action":    action,
        })
        save_json(HISTORY_FILE, history)
# ─────────────────────────────────────────────
#  Shipment Review Panel  (History)
#  Uses binary search on sorted item codes
# ─────────────────────────────────────────────
 
class ViewHistory(QWidget):
    """
    History panel.
    Search uses binary search (O log n) on item codes sorted alphabetically.
    Falls back to linear scan for status/action column.
    """
    main_btn_style = """
                QPushButton {
                    background-color: #800000; color: white;
                    padding: 4px 12px; border-radius: 18px;
                    font-size: 13px; min-width: 75px; min-height: 28px;
                }
                QPushButton:hover { background-color: #a00000; }
                QPushButton:pressed { background-color: #600000; }
            """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._history: list = []          # raw history
        self._sorted_history: list = []   # sorted by item_code for binary search
        self._build_ui()
        self._load_history()
 
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
 
        inner = QWidget()
        inner.setStyleSheet("""
            QWidget { background-color: white; border-radius: 25px; margin: 10px; }
        """)
        il = QVBoxLayout(inner)
        il.setContentsMargins(20, 20, 20, 20)
 
        # ── Header
        hc = QWidget()
        hl = QHBoxLayout(hc)
        hl.setContentsMargins(0, 0, 0, 0)
        logo = QLabel("Switft Route")
        logo.setFont(QFont("Helvetica", 20))
        logo.setStyleSheet("color: #800000; font-weight: bold;")
        logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hl.addWidget(logo)
        hl.addStretch()
 
        slabel = QLabel("History")
        slabel.setFont(QFont("Helvetica", 15))
        slabel.setStyleSheet("""
            color: white; background-color: #800000;
            border-radius: 20px; padding: 10px 25px; font-size: 16px;
        """)
        slabel.setAlignment(Qt.AlignCenter)
 
        # ── Search bar + info label
        search_row = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Item Code (binary search) or Status")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 12px; border-radius: 20px;
                border: 1px solid #d9bebe; background-color: white;
                font-size: 14px; margin-bottom: 10px;
            }
        """)
        self.search_bar.setFixedWidth(380)
        self.search_bar.setMinimumHeight(36)
        self.search_bar.textChanged.connect(self._search)
 
        self.search_info = QLabel("🔍 Binary search active on item codes")
        self.search_info.setStyleSheet("color: #888; font-size: 11px; padding-left: 8px;")
 
        search_row.addWidget(self.search_bar)
        search_row.addWidget(self.search_info)
        search_row.addStretch()
 
        # ── Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Item Code", "Deadline", "Category", "Date & Time", "Status"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fcecec; border: none;
                border-radius: 15px; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #fcecec; color: black;
                font-weight: bold; padding: 8px 10px; border: none;
                font-size: 14px; font-family: Helvetica;
            }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(70)
        self.table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table.setMinimumHeight(200)
 
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        
        # ── Footer
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Helvetica"))
        back_btn.setStyleSheet("main_btn_style")
        back_btn.clicked.connect(self._go_back)
 
        manage_btn = QPushButton("Manage Shipments")
        manage_btn.setFont(QFont("Helvetica"))
        manage_btn.setStyleSheet("main_btn_style")
        manage_btn.clicked.connect(
            lambda: self.parent_window.setCentralWidget(
                ShipmentDashboard(self.parent_window)))
 
        footer = QWidget()
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.addWidget(manage_btn)
        fl.addStretch()
        fl.addWidget(back_btn)
        fl.addStretch()
       
        fl.addSpacing(10)
    
 
        il.addWidget(hc)
        il.addWidget(slabel)
        il.addLayout(search_row)
        il.addWidget(self.table)
        il.addWidget(footer, alignment=Qt.AlignRight)
 
        main_layout.addWidget(inner)
 
    # ── Data ──────────────────────────────────────────────────────
 
    def _load_history(self):
        self._history = load_json(HISTORY_FILE, [])
        # Sort a copy by item_code for binary search
        self._sorted_history = sorted(
            self._history, key=lambda x: x["item_code"].lower())
        self._populate_table(self._history)
 
    def _populate_table(self, records: list):
        self.table.setRowCount(0)
        for entry in records:
            self._add_row(entry)
 
    def _add_row(self, entry: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 60)
 
        def cell(text):
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item
 
        self.table.setItem(row, 0, cell(entry.get("item_code", "")))
        self.table.setItem(row, 1, cell(entry.get("deadline", "—")))
        self.table.setItem(row, 2, cell(entry.get("category", "—")))
        self.table.setItem(row, 3, cell(entry.get("date_time", "")))
 
        action = entry.get("action", "")
        status_item = cell(action)
        if action == "Delivered":
            status_item.setForeground(QColor("#27ae60"))
        elif action == "Returned":
            status_item.setForeground(QColor("#c0392b"))
        self.table.setItem(row, 4, status_item)
 
    # ── Search ────────────────────────────────────────────────────
 
    def _search(self, text: str):
        """
        Search strategy:
          - If text looks like an item code (no spaces): binary search O(log n)
          - If text matches a status keyword: linear scan on action field O(n)
          - Empty: show all
        """
        text = text.strip()
        if not text:
            self._populate_table(self._history)
            self.search_info.setText("🔍 Binary search active on item codes")
            return
 
        status_keywords = {"delivered", "returned"}
        if text.lower() in status_keywords:
            # linear scan on action
            results = [e for e in self._history
                       if e.get("action", "").lower() == text.lower()]
            self.search_info.setText(f"⟳ Linear scan on Status — {len(results)} result(s)")
        else:
            # binary search on item_code
            results = binary_search_history(self._sorted_history, text)
            if not results:
                # fallback: partial linear scan
                results = [e for e in self._history
                           if text.lower() in e.get("item_code", "").lower()]
                self.search_info.setText(f"⟳ Fallback linear scan — {len(results)} result(s)")
            else:
                self.search_info.setText(
                    f"✓ Binary search — {len(results)} result(s) found")
 
        self._populate_table(results)
 
    def _go_back(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(self.parent_window.PAGE_HOME)
