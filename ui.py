from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QInputDialog, QLineEdit, QHeaderView, QDialog,
    QFormLayout, QDateEdit, QComboBox, QDialogButtonBox, QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget
)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QBrush, QPen,
    QLinearGradient, QPixmap, QPalette)
from PyQt5.QtCore import Qt, QSize, QDate
from datetime import datetime, date
from function import *
import sys
import json
import os


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
 
# Assets
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BACKDROP_IMG = os.path.join(BASE_DIR, "assets/backdrop.png")
EYE_IMG      = os.path.join(BASE_DIR, "assets/eye.png")
 
ORANGE   = "#f97316"
ORANGE_H = "#fb923c"   # hover
 
 
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
        eye_pix = QPixmap("eye.png")
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
        
# Main Window
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
        self.shipment_page = ShipmentManager(self)
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
 
class ShipmentManager(QWidget):
    """
    Main panel for active shipments.
    Table columns: #Rank | Item Code | Deadline | Days Left | Priority | Category | Options
    Sorted by nearest deadline using brute-force bubble sort.
    """
    COLS = ["Rank", "Item Code", "Deadline", "Days Left", "Priority", "Category", "Options"]
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.shipments: list = load_json(SHIPMENTS_FILE, [])
        self._build_ui()
        self._refresh_table()
 
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
        logo = QLabel("Swift Route")
        logo.setFont(QFont("Helvetica", 20))
        logo.setStyleSheet("color: #800000; font-weight: bold;")
        logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hl.addWidget(logo)
        hl.addStretch()
 
        # ── Section label
        slabel = QLabel("Shipment Manager  •  Priority View")
        slabel.setFont(QFont("Helvetica", 15))
        slabel.setStyleSheet("""
            color: white; background-color: #800000;
            border-radius: 20px; padding: 5px 15px; font-size: 16px;
        """)
        slabel.setAlignment(Qt.AlignCenter)
 
        # ── Legend row
        legend_row = QHBoxLayout()
        legend_row.setSpacing(10)
        legend_row.addStretch()
        for p in PRIORITY_ORDER:
            badge = QLabel(p)
            bg = PRIORITY_COLORS[p]
            fg = PRIORITY_TEXT_COLORS[p]
            badge.setStyleSheet(f"""
                background-color:{bg}; color:{fg};
                border-radius:8px; padding:3px 10px;
                font-size:11px; font-weight:bold;
            """)
            legend_row.addWidget(badge)
        legend_row.addStretch()
 
        # ── Buttons
        main_btn_style = """
            QPushButton {
                background-color: #d9bebe; color: #800000;
                border-radius: 10px; padding: 10px 30px; font-size: 16px;
            }
            QPushButton:hover { background-color: #e9f5f3; }
        """
        add_btn = QPushButton("+ Add Shipment")
        add_btn.setStyleSheet(main_btn_style)
        add_btn.clicked.connect(self._add_shipment)
 
        review_btn = QPushButton("Shipment Review →")
        review_btn.setStyleSheet(main_btn_style)
        review_btn.clicked.connect(
            lambda: self.parent_window.setCentralWidget(ViewHistory(self.parent_window)))
 
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(add_btn)
        btn_row.addSpacing(30)
        btn_row.addWidget(review_btn)
        btn_row.addStretch()
 
        # ── Table
        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fcecec;
                border: none; border-radius: 15px; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #800000; color: white;
                font-weight: bold; padding: 8px 10px;
                border: none; border-radius: 10px;
                font-size: 14px; font-family: Helvetica;
            }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(70)
        self.table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table.setMinimumHeight(200)
 
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Rank
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)           # Item Code
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Deadline
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Days Left
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Priority
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Category
        hdr.setSectionResizeMode(6, QHeaderView.Stretch)           # Options
 
        # ── Count label & footer
        self.count_label = QLabel()
        self.count_label.setFont(QFont("Helvetica", 10))
        self.count_label.setStyleSheet("color: black;")
 
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Helvetica"))
        back_btn.setStyleSheet(main_btn_style)
        back_btn.clicked.connect(self._go_back)
 
        footer = QWidget()
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.addWidget(self.count_label)
        fl.addStretch()
        fl.addWidget(back_btn)
 
        il.addWidget(hc)
        il.addWidget(slabel, alignment=Qt.AlignHCenter)
        il.addLayout(legend_row)
        il.addLayout(btn_row)
        il.addWidget(self.table)
        il.addWidget(footer)
 
        main_layout.addWidget(inner)
 
    # ── Table rendering ────────────────────────────────────────────
 
    def _refresh_table(self):
        """Recompute days, bubble-sort, and redraw the whole table."""
        for s in self.shipments:
            s["days_remaining"] = compute_days_remaining(s["deadline"])
 
        sorted_shipments = brute_force_sort(self.shipments)
 
        self.table.setRowCount(0)
        for rank, s in enumerate(sorted_shipments, 1):
            self._add_table_row(rank, s)
 
        self._update_count()
 
    def _add_table_row(self, rank: int, s: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 70)
 
        days     = s["days_remaining"]
        priority = get_priority(days)
 
        if days < 0:
            days_str = f"{abs(days)}d overdue"
        elif days == 0:
            days_str = "Today"
        else:
            days_str = f"{days}d left"
 
        def cell(text, color=None):
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(Qt.AlignCenter)
            if color:
                item.setForeground(QColor(color))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item
 
        self.table.setItem(row, 0, cell(rank))
        self.table.setItem(row, 1, cell(s["item_code"]))
        self.table.setItem(row, 2, cell(s["deadline"]))
        self.table.setItem(row, 3, cell(days_str,
            PRIORITY_COLORS.get(priority)))
        self.table.setCellWidget(row, 4, make_priority_badge(priority))
        self.table.setItem(row, 5, cell(s.get("category", "Standard")))
 
        # ── Option buttons
        opt = QWidget()
        opt.setStyleSheet("background-color: #fcecec;")
        hl = QHBoxLayout(opt)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(6)
        hl.setAlignment(Qt.AlignCenter)
 
        btn_s = """
            QPushButton {
                background-color: #800000; color: white;
                padding: 4px 12px; border-radius: 18px;
                font-size: 13px; min-width: 75px; min-height: 28px;
            }
            QPushButton:hover { background-color: #a00000; }
            QPushButton:pressed { background-color: #600000; }
        """
 
        deliver_btn = QPushButton("Deliver")
        deliver_btn.setStyleSheet(btn_s)
        deliver_btn.clicked.connect(
            lambda _, sid=s["id"]: self._confirm_action(sid, "Delivered"))
 
        return_btn = QPushButton("Return")
        return_btn.setStyleSheet(btn_s)
        return_btn.clicked.connect(
            lambda _, sid=s["id"]: self._confirm_action(sid, "Returned"))
 
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(btn_s)
        edit_btn.clicked.connect(
            lambda _, sid=s["id"]: self._edit_shipment(sid))
 
        trash_btn = QPushButton("✕")
        trash_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #800000;
                border: 1px solid #800000; border-radius: 14px;
                font-size: 14px; min-width: 28px; min-height: 28px;
            }
            QPushButton:hover { background-color: #800000; color: white; }
        """)
        trash_btn.clicked.connect(
            lambda _, sid=s["id"]: self._delete_shipment(sid))
 
        hl.addWidget(deliver_btn)
        hl.addWidget(return_btn)
        hl.addWidget(edit_btn)
        hl.addWidget(trash_btn)
        self.table.setCellWidget(row, 6, opt)
 
    # CRUD actions 
 
    def _add_shipment(self):
        dlg = ShipmentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.get_values()
            new_id = max((s["id"] for s in self.shipments), default=0) + 1
            self.shipments.append({
                "id":       new_id,
                "item_code": vals["item_code"],
                "deadline":  vals["deadline"],
                "category":  vals["category"],
                "added_at":  datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            })
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh_table()
 
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
            self._refresh_table()
 
    def _delete_shipment(self, sid: int):
        s = next((x for x in self.shipments if x["id"] == sid), None)
        if not s:
            return
        r = QMessageBox.question(self, "Delete",
            f"Remove shipment '{s['item_code']}'?",
            QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            self.shipments = [x for x in self.shipments if x["id"] != sid]
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh_table()
 
    def _confirm_action(self, sid: int, action: str):
        s = next((x for x in self.shipments if x["id"] == sid), None)
        if not s:
            return
        r = QMessageBox.question(self, "Confirm",
            f"Mark '{s['item_code']}' as {action}?",
            QMessageBox.Ok | QMessageBox.Cancel)
        if r == QMessageBox.Ok:
            self._move_to_history(s, action)
            self.shipments = [x for x in self.shipments if x["id"] != sid]
            save_json(SHIPMENTS_FILE, self.shipments)
            self._refresh_table()
 
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
 
    def _update_count(self):
        self.count_label.setText(f"Active Shipments: {len(self.shipments)}")
 
    def _go_back(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(self.parent_window.PAGE_HOME)

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
                ShipmentManager(self.parent_window)))
 
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
