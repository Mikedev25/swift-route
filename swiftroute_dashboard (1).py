"""
SwiftRoute — Integrated Dashboard
Design  : swiftroute_dashboard.py  (black header card, stat cards, clean table)
Logic   : ui.py  (ShipmentDialog, CRUD, bubble-sort, binary-search history,
                  deliver/return/edit/delete actions, JSON persistence)

Requires:
  function.py   — load_json, save_json, compute_days_remaining,
                  brute_force_sort, get_priority, binary_search_history,
                  PRIORITY_COLORS, PRIORITY_TEXT_COLORS, PRIORITY_ORDER,
                  SHIPMENTS_FILE, HISTORY_FILE
  assets/eye.png
  assets/backdrop.png
"""

import sys
import os
from datetime import datetime, date

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy,
    QFrame, QGraphicsDropShadowEffect, QStackedWidget,
    QDialog, QFormLayout, QDateEdit, QComboBox,
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QBrush, QPixmap,
    QLinearGradient, QPainterPath, QIcon
)
from PyQt5.QtCore import Qt, QDate

from function import (
    load_json, save_json,
    compute_days_remaining, brute_force_sort, get_priority,
    binary_search_history,
    PRIORITY_COLORS, PRIORITY_TEXT_COLORS, PRIORITY_ORDER,
    SHIPMENTS_FILE, HISTORY_FILE,
)

# ── Asset paths ────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
BACKDROP_IMG = os.path.join(BASE_DIR, "assets", "backdrop.png")
EYE_IMG      = os.path.join(BASE_DIR, "assets", "eye.png")

# ── Palette ────────────────────────────────────────────────────────────────
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


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _make_badge(text: str, bg: str, fg: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
    lbl.setStyleSheet(
        f"background-color:{bg}; color:{fg}; border-radius:10px; padding:3px 12px;")
    lbl.setFixedHeight(26)
    return lbl


# ══════════════════════════════════════════════════════════════════════════════
#  SHIPMENT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ShipmentDialog(QDialog):
    CATEGORIES = ["Standard", "Express", "Fragile",
                  "Refrigerated", "Hazmat", "Other"]

    def __init__(self, parent=None, shipment: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Shipment" if shipment else "New Shipment")
        self.setMinimumWidth(400)
        self._build_ui(shipment)

    def _build_ui(self, shipment):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g. SHP-20240001")
        if shipment:
            self.code_input.setText(shipment.get("item_code", ""))
        layout.addRow("Item Code:", self.code_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setMinimumDate(QDate.currentDate())
        if shipment and shipment.get("deadline"):
            self.date_input.setDate(
                QDate.fromString(shipment["deadline"], "yyyy-MM-dd"))
        else:
            self.date_input.setDate(QDate.currentDate().addDays(3))
        layout.addRow("Deadline:", self.date_input)

        self.cat_input = QComboBox()
        self.cat_input.addItems(self.CATEGORIES)
        if shipment and shipment.get("category") in self.CATEGORIES:
            self.cat_input.setCurrentIndex(
                self.CATEGORIES.index(shipment["category"]))
        layout.addRow("Category:", self.cat_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setStyleSheet(f"""
            QDialog  {{ background: white; }}
            QLabel   {{ font-size: 13px; color: #333; font-family: 'Segoe UI'; }}
            QLineEdit, QDateEdit, QComboBox {{
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 6px 10px; font-size: 13px; font-family: 'Segoe UI';
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
                border-color: {ORANGE};
            }}
            QPushButton {{
                background-color: {ORANGE}; color: white;
                border-radius: 10px; padding: 6px 18px;
                font-size: 13px; font-family: 'Segoe UI';
            }}
            QPushButton:hover {{ background-color: {ORANGE_H}; }}
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


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER CARD
# ══════════════════════════════════════════════════════════════════════════════

class HeaderCard(QWidget):
    def __init__(self, title: str, on_new_shipment=None,
                 show_history_btn=False, on_history=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(16)

        # Left — logo + title + date
        left = QVBoxLayout()
        left.setSpacing(4)
        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        eye_pix = QPixmap(EYE_IMG)
        logo = QLabel()
        if not eye_pix.isNull():
            logo.setPixmap(
                eye_pix.scaled(36, 36, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation))
        else:
            logo.setFixedSize(36, 36)
            logo.setStyleSheet(f"background:{ORANGE}; border-radius:6px;")
        title_row.addWidget(logo, alignment=Qt.AlignVCenter)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl.setStyleSheet(f"color:{TEXT_WHITE}; background:transparent;")
        title_row.addWidget(lbl, alignment=Qt.AlignVCenter)
        left.addLayout(title_row)

        date_lbl = QLabel(QDate.currentDate().toString("dddd - MMMM d, yyyy"))
        date_lbl.setFont(QFont("Segoe UI", 10))
        date_lbl.setStyleSheet("color:rgba(255,255,255,0.55); background:transparent;")
        left.addWidget(date_lbl)
        layout.addLayout(left, stretch=1)

        # Right — search + action buttons
        right = QHBoxLayout()
        right.setSpacing(10)
        right.setAlignment(Qt.AlignVCenter)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search item code…")
        self.search.setFixedHeight(40)
        self.search.setMinimumWidth(200)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background-color:{BG_SEARCH}; color:{TEXT_WHITE};
                border:none; border-radius:20px;
                padding:0 16px; font-size:13px; font-family:'Segoe UI';
            }}
        """)
        right.addWidget(self.search)

        if show_history_btn and on_history:
            hist_btn = QPushButton("📋  View History")
            hist_btn.setFixedHeight(40)
            hist_btn.setCursor(Qt.PointingHandCursor)
            hist_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:rgba(255,255,255,0.12); color:white;
                    border:1px solid rgba(255,255,255,0.3); border-radius:20px;
                    font-size:13px; font-family:'Segoe UI'; padding:0 16px;
                }}
                QPushButton:hover {{ background-color:rgba(255,255,255,0.22); }}
            """)
            hist_btn.clicked.connect(on_history)
            right.addWidget(hist_btn)

        if on_new_shipment:
            new_btn = QPushButton("\u2295  New Shipment")
            new_btn.setFixedHeight(40)
            new_btn.setCursor(Qt.PointingHandCursor)
            new_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:{ORANGE}; color:white; border:none;
                    border-radius:20px; font-size:13px; font-weight:700;
                    font-family:'Segoe UI'; padding:0 20px;
                }}
                QPushButton:hover   {{ background-color:{ORANGE_H}; }}
                QPushButton:pressed {{ background-color:#c85c0a; }}
            """)
            new_btn.clicked.connect(on_new_shipment)
            right.addWidget(new_btn)

        layout.addLayout(right)

        self.corner_badge = QLabel("HI  LOW")
        self.corner_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.corner_badge.setAlignment(Qt.AlignCenter)
        self.corner_badge.setStyleSheet(
            f"background-color:{PURPLE}; color:white; padding:3px 10px; letter-spacing:1px;")
        self.corner_badge.setParent(self)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        p.fillPath(path, QColor(BG_HEADER))
        p.end()

    def resizeEvent(self, event):
        bw = self.corner_badge.sizeHint().width() + 16
        self.corner_badge.setGeometry(self.width() - bw, 0, bw, 24)
        super().resizeEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════════════════════════════════════

class StatCard(QWidget):
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


# ══════════════════════════════════════════════════════════════════════════════
#  SHIPMENT TABLE  (dashboard style + CRUD from ui.py)
# ══════════════════════════════════════════════════════════════════════════════

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

    # ── Public ────────────────────────────────────────────────────────────

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

    # ── Row ───────────────────────────────────────────────────────────────

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
            cell(s["item_code"], Qt.AlignLeft | Qt.AlignVCenter))
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


# ══════════════════════════════════════════════════════════════════════════════
#  SHIPMENT DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════

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

        self.header = HeaderCard(
            title="Your Dashboard",
            on_new_shipment=self._add_shipment,
            show_history_btn=True,
            on_history=self.on_history,
        )
        self.header.search.textChanged.connect(self._on_search)
        root.addWidget(self.header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.card_total    = StatCard("Total Shipments", 0, ORANGE)
        self.card_delivered = StatCard("Delivered",      0, "#22c55e")
        self.card_pending   = StatCard("Pending",        0, ORANGE)
        self.card_overdue  = StatCard("Overdue",         0, PURPLE)
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
            back_btn = QPushButton("← Back to Home")
            back_btn.setFixedHeight(36)
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

    # ── CRUD ──────────────────────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY PAGE  (binary-search from ui.py + dashboard style)
# ══════════════════════════════════════════════════════════════════════════════

class ViewHistory(QWidget):
    COLS = ["Item Code", "Deadline", "Category", "Date & Time", "Status"]

    def __init__(self, on_back=None, on_manage=None, parent=None):
        super().__init__(parent)
        self._history:        list = []
        self._sorted_history: list = []
        self.setStyleSheet(f"background-color:{BG_MAIN};")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.header = HeaderCard(title="Shipment History")
        self.header.search.setPlaceholderText(
            "Search by item code or status (Delivered / Returned)…")
        self.header.search.textChanged.connect(self._search)
        root.addWidget(self.header)

        self.search_info = QLabel("🔍 Binary search active on item codes")
        self.search_info.setFont(QFont("Segoe UI", 10))
        self.search_info.setStyleSheet(
            f"color:{TEXT_GRAY}; background:transparent;")
        root.addWidget(self.search_info)

        # Table card
        table_card = QWidget()
        table_card.setStyleSheet(
            f"background-color:{BG_CARD}; border-radius:16px;")
        tc_shadow = QGraphicsDropShadowEffect(table_card)
        tc_shadow.setBlurRadius(20)
        tc_shadow.setOffset(0, 4)
        tc_shadow.setColor(QColor(0, 0, 0, 25))
        table_card.setGraphicsEffect(tc_shadow)

        tc_lay = QVBoxLayout(table_card)
        tc_lay.setContentsMargins(20, 16, 20, 16)
        tc_lay.setSpacing(10)

        hdr_row = QHBoxLayout()
        t_lbl = QLabel("History Log")
        t_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        t_lbl.setStyleSheet(f"color:{TEXT_DARK}; background:transparent;")
        hdr_row.addWidget(t_lbl)
        hdr_row.addStretch()
        tc_lay.addLayout(hdr_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color:{BORDER};")
        tc_lay.addWidget(line)

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
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        tc_lay.addWidget(self.table)

        root.addWidget(table_card, stretch=1)

        # Footer
        footer = QHBoxLayout()
        if on_manage:
            mgr_btn = QPushButton("Manage Shipments →")
            mgr_btn.setFixedHeight(36)
            mgr_btn.setCursor(Qt.PointingHandCursor)
            mgr_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:{ORANGE}; color:white; border:none;
                    border-radius:18px; font-size:12px;
                    font-family:'Segoe UI'; padding:0 18px;
                }}
                QPushButton:hover {{ background-color:{ORANGE_H}; }}
            """)
            mgr_btn.clicked.connect(on_manage)
            footer.addWidget(mgr_btn)
        footer.addStretch()
        if on_back:
            back_btn = QPushButton("← Back to Home")
            back_btn.setFixedHeight(36)
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
            footer.addWidget(back_btn)
        root.addLayout(footer)

        self._load_history()

    def _load_history(self):
        self._history = load_json(HISTORY_FILE, [])
        self._sorted_history = sorted(
            self._history, key=lambda x: x["item_code"].lower())
        self._populate(self._history)

    def reload(self):
        self._load_history()

    def _populate(self, records: list):
        self.table.setRowCount(0)
        for entry in records:
            self._add_row(entry)

    def _add_row(self, entry: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 52)

        def cell(text, align=Qt.AlignCenter):
            item = QTableWidgetItem(str(text))
            item.setTextAlignment(align)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        self.table.setItem(
            row, 0, cell(entry.get("item_code", ""),
                         Qt.AlignLeft | Qt.AlignVCenter))
        self.table.setItem(row, 1, cell(entry.get("deadline", "—")))
        self.table.setItem(row, 2, cell(entry.get("category", "—")))
        self.table.setItem(row, 3, cell(entry.get("date_time", "")))

        action = entry.get("action", "")
        status_item = cell(action)
        if action == "Delivered":
            status_item.setForeground(QColor("#22c55e"))
        elif action == "Returned":
            status_item.setForeground(QColor("#dc2626"))
        self.table.setItem(row, 4, status_item)

    def _search(self, text: str):
        text = text.strip()
        if not text:
            self._populate(self._history)
            self.search_info.setText(
                "🔍 Binary search active on item codes")
            return

        status_keywords = {"delivered", "returned"}
        if text.lower() in status_keywords:
            results = [e for e in self._history
                       if e.get("action", "").lower() == text.lower()]
            self.search_info.setText(
                f"⟳ Linear scan on Status — {len(results)} result(s)")
        else:
            results = binary_search_history(self._sorted_history, text)
            if not results:
                results = [e for e in self._history
                           if text.lower() in e.get("item_code", "").lower()]
                self.search_info.setText(
                    f"⟳ Fallback linear scan — {len(results)} result(s)")
            else:
                self.search_info.setText(
                    f"✓ Binary search — {len(results)} result(s) found")
        self._populate(results)


# ══════════════════════════════════════════════════════════════════════════════
#  WELCOME PAGE  (backdrop hero from ui.py)
# ══════════════════════════════════════════════════════════════════════════════

class _BackdropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(BACKDROP_IMG)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation)
            x = (scaled.width()  - self.width())  // 2
            y = (scaled.height() - self.height()) // 2
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor(0, 0, 0, 200))
        grad.setColorAt(0.5, QColor(0, 0, 0, 100))
        grad.setColorAt(1.0, QColor(0, 0, 0,  60))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawRect(self.rect())
        p.setBrush(QBrush(QColor(0, 0, 0, 80)))
        p.drawRect(0, 0, self.width(), 72)
        p.end()


class WelcomePage(QWidget):
    def __init__(self, on_manage, on_history, parent=None):
        super().__init__(parent)
        self._backdrop = _BackdropWidget(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar
        nav = QWidget()
        nav.setFixedHeight(72)
        nav.setAttribute(Qt.WA_TranslucentBackground)
        nl = QHBoxLayout(nav)
        nl.setContentsMargins(32, 0, 32, 0)
        nl.setSpacing(12)
        eye_pix = QPixmap(EYE_IMG)
        nav_logo = QLabel()
        if not eye_pix.isNull():
            nav_logo.setPixmap(
                eye_pix.scaled(44, 44, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation))
        else:
            nav_logo.setFixedSize(44, 44)
            nav_logo.setStyleSheet(f"background:{ORANGE}; border-radius:8px;")
        nl.addWidget(nav_logo, alignment=Qt.AlignVCenter)
        brand = QLabel("SWIFT ROUTE")
        brand.setFont(QFont("Segoe UI", 13, QFont.Bold))
        brand.setStyleSheet(
            "color:white; letter-spacing:2px; background:transparent;")
        nl.addWidget(brand, alignment=Qt.AlignVCenter)
        nl.addStretch()
        root.addWidget(nav)

        # Hero
        hero_row = QHBoxLayout()
        hero_row.setContentsMargins(48, 0, 48, 0)
        hero_row.setSpacing(32)

        text_w = QWidget()
        text_w.setAttribute(Qt.WA_TranslucentBackground)
        text_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tl = QVBoxLayout(text_w)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setAlignment(Qt.AlignVCenter)
        self._headline = QLabel("Top-notch\nlogistic services")
        self._headline.setFont(QFont("Segoe UI", 48, QFont.Bold))
        self._headline.setStyleSheet(f"color:{ORANGE}; background:transparent;")
        tl.addWidget(self._headline)
        tl.addSpacing(18)
        self._sub = QLabel(
            "We take pride in delivering shipments\n"
            "expressively to the comfort of your\nhomes.")
        self._sub.setFont(QFont("Segoe UI", 13))
        self._sub.setStyleSheet(
            "color:rgba(255,255,255,0.85); background:transparent;")
        tl.addWidget(self._sub)
        hero_row.addWidget(text_w, stretch=3)

        btn_w = QWidget()
        btn_w.setAttribute(Qt.WA_TranslucentBackground)
        btn_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bl = QVBoxLayout(btn_w)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(16)
        bl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._hero_btns = []
        for label, cb in [("Manage Shipments", on_manage),
                           ("Shipment History", on_history)]:
            btn = QPushButton(label)
            btn.setFixedHeight(48)
            btn.setMinimumWidth(220)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setAttribute(Qt.WA_TranslucentBackground)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:{ORANGE}; color:white; border:none;
                    border-radius:24px; font-size:14px; font-weight:700;
                    font-family:'Segoe UI'; padding:0 28px;
                }}
                QPushButton:hover   {{ background-color:{ORANGE_H}; }}
                QPushButton:pressed {{ background-color:#c85c0a; }}
            """)
            btn.clicked.connect(cb)
            sh = QGraphicsDropShadowEffect()
            sh.setBlurRadius(24)
            sh.setOffset(0, 4)
            sh.setColor(QColor(249, 115, 22, 140))
            btn.setGraphicsEffect(sh)
            self._hero_btns.append(btn)
            bl.addWidget(btn, alignment=Qt.AlignRight)
        hero_row.addWidget(btn_w, stretch=2)

        hero_container = QWidget()
        hero_container.setAttribute(Qt.WA_TranslucentBackground)
        hero_container.setLayout(hero_row)
        hero_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(hero_container, stretch=1)

    def resizeEvent(self, event):
        self._backdrop.setGeometry(0, 0, self.width(), self.height())
        scale = self.width() / 1140.0
        self._headline.setFont(
            QFont("Segoe UI", max(12, int(48 * scale)), QFont.Bold))
        self._sub.setFont(QFont("Segoe UI", max(6, int(13 * scale))))
        for btn in self._hero_btns:
            h = max(24, int(48 * scale))
            w = max(110, int(220 * scale))
            r = h // 2
            btn.setFixedHeight(h)
            btn.setMinimumWidth(w)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:{ORANGE}; color:white; border:none;
                    border-radius:{r}px;
                    font-size:{max(7, int(14*scale))}px;
                    font-weight:700; font-family:'Segoe UI';
                    padding:0 {max(14, int(28*scale))}px;
                }}
                QPushButton:hover   {{ background-color:{ORANGE_H}; }}
                QPushButton:pressed {{ background-color:#c85c0a; }}
            """)
        super().resizeEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QWidget):
    PAGE_HOME      = 0
    PAGE_DASHBOARD = 1
    PAGE_HISTORY   = 2

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SwiftRoute — Logistics Platform")
        self.setWindowIcon(QIcon(EYE_IMG))
        self.setMinimumSize(1140, 620)
        self.resize(1200, 700)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.welcome = WelcomePage(
            on_manage=self.go_to_dashboard,
            on_history=self.go_to_history,
        )
        self.stack.addWidget(self.welcome)           # 0

        self.dashboard = ShipmentDashboard(
            on_back=self.go_home,
            on_history=self.go_to_history,
        )
        self.stack.addWidget(self.dashboard)         # 1

        self.history = ViewHistory(
            on_back=self.go_home,
            on_manage=self.go_to_dashboard,
        )
        self.stack.addWidget(self.history)           # 2

        self.stack.setCurrentIndex(self.PAGE_HOME)

    def go_home(self):
        self.stack.setCurrentIndex(self.PAGE_HOME)

    def go_to_dashboard(self):
        self.dashboard.shipments = load_json(SHIPMENTS_FILE, [])
        self.dashboard._refresh()
        self.stack.setCurrentIndex(self.PAGE_DASHBOARD)

    def go_to_history(self):
        self.history.reload()
        self.stack.setCurrentIndex(self.PAGE_HISTORY)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
