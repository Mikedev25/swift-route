from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QPushButton, QMessageBox,
                             QInputDialog, QLineEdit, QHeaderView)
from PyQt5.QtGui import QIcon 
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from datetime import datetime
import sys
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Creating a Main Window
        self.setWindowTitle("ShopLogix")
        self.setGeometry(100, 100, 1200, 600)
        # Creating a Window Icon
        self.setWindowIcon(QIcon("C:/Users/Desiree Lope/Downloads/package.png"))
        #For History
        self.codes_file = "item_codes.json"
        self.history_file = "history.json"
        self.initUI()
    # Initializes User Interface       
    def initUI(self):
        self.welcome_panel()
    # Creating Welcome Panel    
    def welcome_panel(self):
        #creating a main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        #for the left panel
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: white;" \
                                 "border-top-left-radius: 25px;" \
                                 "border-bottom-left-radius: 25px")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 0, 20)  # Padding on left and top
        left_layout.setSpacing(0)

        label = QLabel("ShopLogix")
        label.setFont(QFont("Helvetica", 20))
        label.setStyleSheet("color: #800000;"
                            "font-weight: bold;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        #container of the ShopLogix label
        header_container = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        header_layout.addWidget(label)
        header_container.setLayout(header_layout)    

        #container for the Welcome Label
        wel_container = QWidget()
        wel_container.setStyleSheet("background-color:#800000;"\
                                "border-radius: 20px;"\
                                "width: 40;"\
                                "height: 40;")
        wel_container.setFixedSize(600,400)
        welcome_layout = QVBoxLayout(wel_container)
        welcome_layout.setContentsMargins(40, 40, 40, 40)  # Padding inside the red box
        welcome_layout.setAlignment(Qt.AlignCenter)
        wel_container.setLayout(welcome_layout)
        
        #welcome label
        welcome_label = QLabel("Welcome to\nShopLogix")
        welcome_label.setFont(QFont("Helvetica", 45))
        welcome_label.setStyleSheet("color: white;")
        welcome_label.setAlignment(Qt.AlignCenter)

        welcome_layout.addWidget(welcome_label)

        left_layout.addWidget(header_container)
        left_layout.addStretch()
        left_layout.addWidget(wel_container, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        #for the right panel
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color:  #f1d1d1;" \
                                  "border-top-right-radius: 25px; " \
                                  "border-bottom-right-radius: 25px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)

        btn_style ="""
            QPushButton {
                background-color: #800000;
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 16px;
                width: 200px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """

        start_btn = QPushButton("Manage Shipments")
        start_btn.setStyleSheet(btn_style)
        start_btn.clicked.connect(lambda: self.setCentralWidget(StartPanel(self)))

        review_btn = QPushButton("Review Shipments")
        review_btn.setStyleSheet(btn_style)
        review_btn.clicked.connect(lambda: self.setCentralWidget(ShipmentReview(self)))

        right_layout.addWidget(start_btn)
        right_layout.addSpacing(20)
        right_layout.addWidget(review_btn)

        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)

class StartPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.item_codes = []  # List to store entered item codes
        self.codes_file = "item_codes.json"  # File to store codes
        self.history_file = "history.json"  # File to store shipment history
        self.initUI() # Initializes User Interface
    
    def initUI(self):
        # Creating Table for Item Codes etc.
        self.table = QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(["Item Code", "Date & Time", "Option"])
        self.table.setStyleSheet("""
                            QTableWidget {
                                background-color: #fcecec;
                                border: none;
                                border-radius: 15px;
                                font-size: 14px;                                                             
                                }
                            QHeaderView::section {
                                background-color: #800000;
                                color: white;
                                font-weight: bold;
                                padding: 8px 10px;
                                border: none;
                                border-radius: 10px;
                                font-size: 14px;
                                font-family: Helvetica;
                                }
                            QTableWidget::item {
                                padding: 5px;
                                }
                                """)
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table.setMinimumHeight(200)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(70)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # Item Code column
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Date & Time column
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Option column
        
        # Create the item counter label before using it
        self.count_label = QLabel()
        self.count_label.setFont(QFont("Helvetica", 10))
        self.count_label.setStyleSheet("color: black;")
        
        # Load existing codes when starting
        self.load_codes()
        
        # Main layout for the entire panel
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the inner frame
        inner_frame = QWidget()
        inner_frame.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 25px;
                margin: 10px;                  
            }
        """)
        
        # Layout for the inner frame
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with ShopLogix label
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("ShopLogix")
        label.setFont(QFont("Helvetica", 20))
        label.setStyleSheet("color: #800000; font-weight: bold;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        header_layout.addWidget(label)
        header_layout.addStretch()
        header_container.setLayout(header_layout)

        # Shipment Manager Label 
        slabel = QLabel("Shipment Manager")
        slabel.setFont(QFont("Helvetica", 15))
        slabel.setStyleSheet("""
            color: white;
            background-color: #800000;
            border-radius: 20px;
            padding: 5px 15px;
            font-size: 16px;
        """)
        slabel.setAlignment(Qt.AlignCenter)

        # Button Style
        button_style = """
            QPushButton {
                background-color: #800000;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
            QPushButton:pressed {
                background-color: #600000;
            }
        """
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Helvetica"))
        back_btn.setStyleSheet(button_style)
        back_btn.clicked.connect(self.go_back)

        # Add and Review Button Style 
        main_btn_style = """
            QPushButton {
                background-color: #d9bebe;
                color: #800000;
                border-radius: 10px;
                padding: 10px 30px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e9f5f3;
            }
        """
        # Add Button
        add_btn = QPushButton("Add an Item Code")
        add_btn.setFont(QFont("Helvetica"))
        add_btn.setStyleSheet(main_btn_style)
        add_btn.clicked.connect(self.add_item)
        
        # Review Shipment Button
        review_btn = QPushButton("Shipment Review →")
        review_btn.setFont(QFont("Helvetica"))
        review_btn.setStyleSheet(main_btn_style)
        review_btn.clicked.connect(lambda: self.parent_window.setCentralWidget(ShipmentReview(self.parent_window)))


        # Button Row Layout
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(add_btn)
        button_row.addSpacing(30)
        button_row.addWidget(review_btn)
        button_row.addStretch()

        # Footer with Back Button and Item Counter
        footer_container = QWidget()
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(0,0,0,0) 
        footer_layout.setSpacing(0)
        footer_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        footer_layout.addWidget(self.count_label)
        footer_layout.addWidget(back_btn)
        footer_container.setLayout(footer_layout)

        # Add header to inner layout
        inner_layout.addWidget(header_container)        
        # Add the Manager Label
        inner_layout.addWidget(slabel, alignment=Qt.AlignHCenter)  
        # Add the Main Buttons
        inner_layout.addLayout(button_row)  
        # Add the Table
        inner_layout.addWidget(self.table)
        # Add footer to inner layout
        inner_layout.addWidget(footer_container, alignment = Qt.AlignRight)
        # Add inner frame to main layout
        main_layout.addWidget(inner_frame)
        # Set the main layout
        self.setLayout(main_layout)

    # Item counter on the bottom
    def update_count_label(self):
        self.count_label.setText(f"Current Items: {self.table.rowCount()}")


    #function of Back Button    
    def go_back(self):
        if self.parent_window:
            self.parent_window.welcome_panel()
    #function of Add Button
    def add_item(self):
        code, ok = QInputDialog.getText(self, 'ShopLogix', 'Enter the Item Code:',
                                     QLineEdit.Normal)
        if ok and code: 
            self.item_codes.append(code)
            # Save codes after adding new one
            self.save_codes()
            # Add Rows for Added Item Code
            self.add_row(code)
            self.update_count_label()

    def save_codes(self):
        """Save item codes to JSON file"""
        try:
            with open(self.codes_file, 'w') as f:
                json.dump(self.item_codes, f)
        except Exception as e:
            print(f"Error saving codes: {e}")

    def load_codes(self):
        """Load item codes from JSON file"""
        try:
            if os.path.exists(self.codes_file):
                with open(self.codes_file, 'r') as f:
                    self.item_codes = json.load(f)
                    for code in self.item_codes:
                        self.add_row(code)
            self.update_count_label()
        except Exception as e:
            print(f"Error loading codes: {e}")
            self.item_codes = []

    def add_row(self, code):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Item Code
        item_code = QTableWidgetItem(code)
        item_code.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_code)

        # Date and Time
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        item_date = QTableWidgetItem(now)
        item_date.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, item_date)

        # Option Buttons
        option = QWidget()
        option.setStyleSheet("background-color: #fcecec;")
        h_layout = QHBoxLayout(option)
        h_layout.setContentsMargins(0,0,0,0)
        h_layout.setSpacing(10)
        h_layout.setAlignment(Qt.AlignCenter)

        button_style = """
            QPushButton {
                background-color: #800000;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                min-width: 90px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
            QPushButton:pressed {
                background-color: #600000;
            }
        """
        # Creating Deliver Button
        deliver_btn = QPushButton("Deliver")
        deliver_btn.setStyleSheet(button_style)
        deliver_btn.clicked.connect(lambda _, r=row, c=code: self.confirm_action(r, c, "Delivered"))
        # Creating Return Button
        return_btn = QPushButton("Return")
        return_btn.setStyleSheet(button_style)
        return_btn.clicked.connect(lambda _, r=row, c=code: self.confirm_action(r, c, "Returned"))
        # Creating Delete Button (Trash Icon)
        trash_btn = QPushButton()
        trash_btn.setIcon(QIcon("C:/Users/Desiree Lope/Downloads/bin.png"))
        trash_btn.setIconSize(QSize(50,50))
        trash_btn.setFixedSize(40,40)
        trash_btn.setStyleSheet("""
                                QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    }
                                QPushButton: hover {
                                    background-color:  #800000;
                                    border-radius: 18px;
                                }
                                """)
        trash_btn.clicked.connect(lambda _, r=row: self.delete_current_row(r))

        h_layout.addWidget(deliver_btn)
        h_layout.addWidget(return_btn)
        h_layout.addWidget(trash_btn)
 
        option.setLayout(h_layout)
        self.table.setCellWidget(row, 2, option)
        self.table.setRowHeight(row, 70)

    # Function of Trash Button
    def delete_current_row(self, row):
        try:
            item_code_item = self.table.item(row, 0)
            if item_code_item:
                code = item_code_item.text()
                # Remove from self.item_codes
                if code in self.item_codes:
                    self.item_codes.remove(code)
                # Remove from file
                if os.path.exists(self.parent_window.codes_file):
                    with open(self.parent_window.codes_file, 'r') as f:
                        codes_data = json.load(f)
                    if code in codes_data:
                        codes_data.remove(code)
                        with open(self.parent_window.codes_file, 'w') as f:
                            json.dump(codes_data, f, indent=4)
                self.table.removeRow(row)
                self.update_count_label()
            else:
                QMessageBox.warning(self, "Error", "Could not find item code for this row.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not delete item: {e}")

    def confirm_action(self, row, code, action):
        # confirmation dialog
        result = QMessageBox.question(
            self, 
            "Confirmation Action",
            f"Confirm: The item '{code}' has been {action.lower()}?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if result == QMessageBox.Ok:
            self.move_to_history(code, action)
            self.table.removeRow(row)
            # Remove from item_codes and save
            if code in self.item_codes:
                self.item_codes.remove(code)
                self.save_codes()
            
    def move_to_history(self, code, action):
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        history_entry = {
            "item_code": code,
            "date_time": now,
            "action": action  # or "Returned" based on the action
        }
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    history_data = json.load(f)
            else:
                history_data = []

            history_data.append(history_entry)

            with open(self.history_file, "w") as f:
                json.dump(history_data, f, indent=4)

        except Exception as e:
            print(f"Error saving history: {e}")
    
class ShipmentReview(QWidget):
    def __init__(self, parent=None):
        self.parent_window = parent
        super().__init__(parent)
        self.setWindowTitle("Shipment Review")
        self.setGeometry(100, 100, 1200, 600)
        self.initUI()
        self.load_history()

    def initUI(self):
        # Creating a Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Item Code or Status")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 20px;
                border: 1px solid #d9bebe;
                background-color: white;
                font-size: 16px;
                margin-bottom: 10px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)
        self.search_bar.setFixedWidth(300)
        self.search_bar.setMinimumHeight(36)

        # Creating a Table for History
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Item Code", "Date & Time", "Status", ""]) 
        self.table.setStyleSheet("""
                            QTableWidget {
                                background-color: #fcecec;
                                border: none;
                                border-radius: 15px;
                                font-size: 14px;                                                             
                                }
                            QHeaderView::section {
                                background-color: #fcecec;
                                color: black;
                                font-weight: bold;
                                padding: 8px 10px;
                                border: none;
                                font-size: 14px;
                                font-family: Helvetica;
                                }
                            QTableWidget::item {
                                padding: 5px
                                }
                                """)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table.setMinimumHeight(200)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(70)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item Code column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Timestamp column
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Status column
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Trash icon column


        # Placeholder for the Shipment Review UI
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Creating a main container
        inner_frame = QWidget()
        inner_frame.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 25px;
                margin: 10px;                  
            }
        """)
        # Layout for the inner frame
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setContentsMargins(20, 20, 20, 20)

        # Header with ShopLogix label
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # ShopLogix Label
        label = QLabel("ShopLogix")
        label.setFont(QFont("Helvetica", 20))
        label.setStyleSheet("color: #800000; font-weight: bold;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # History Label 
        slabel = QLabel("History")
        slabel.setFont(QFont("Helvetica", 15))
        slabel.setStyleSheet("""
            color: white;
            background-color: #800000;
            border-radius: 20px;
            padding: 10px 25px;
            font-size: 16px;
        """)
        slabel.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(label)
        header_layout.addWidget(slabel)
        header_container.setLayout(header_layout)

        # Creating a Back Button        
        button_style = """
            QPushButton {
                background-color: #800000;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
            QPushButton:pressed {
                background-color: #600000;
            }
        """
        back_btn = QPushButton("← Back")
        back_btn.setFont(QFont("Helvetica"))
        back_btn.setStyleSheet(button_style)
        back_btn.clicked.connect(self.go_back)

        manage_btn = QPushButton("Manage Shipments")
        manage_btn.setFont(QFont("Helvetica"))
        manage_btn.setStyleSheet(button_style)
        manage_btn.clicked.connect(lambda: self.parent_window.setCentralWidget(StartPanel(self.parent_window)))

        # Footer with Manage Shipments and Back Button
        footer_container = QWidget()
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        footer_layout.addWidget(manage_btn)

        footer_layout.addWidget(back_btn)
        footer_container.setLayout(footer_layout)

        # Adding the widgets to the main layout
        inner_layout.addWidget(header_container)
        inner_layout.addWidget(self.search_bar)
        inner_layout.addWidget(self.table)
        inner_layout.addWidget(footer_container, alignment=Qt.AlignRight)
        main_layout.addWidget(inner_frame)
        self.setLayout(main_layout)

    def filter_table(self, text): 
        # Filter table rows based on search text.
        for row in range(self.table.rowCount()):
            match = False
            for col in [0, 2]:  # Item Code and Status columns
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def load_history(self):
        try:
            if os.path.exists(self.parent_window.history_file):
                with open(self.parent_window.history_file, 'r') as f:
                    history_data = json.load(f)
                    for entry in history_data:
                        self.add_row(entry)
        except Exception as e:
            print(f"Error loading history: {e}")

    def add_row(self, entry):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # Item Code
        item_code = QTableWidgetItem(entry["item_code"])
        item_code.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, item_code)
        # Date and Time
        date_time = QTableWidgetItem(entry["date_time"])
        date_time.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, date_time)
        # Status
        status = QTableWidgetItem(entry["action"])
        status.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, status)
        # Empty Column for Trash Icon
        self.table.setItem(row, 3, QTableWidgetItem(""))
        self.table.setRowHeight(row, 70)

        
        # Add trash button
        trash_btn = QPushButton()
        trash_btn.setIcon(QIcon("C:/Users/Desiree Lope/Downloads/bin.png"))
        trash_btn.setIconSize(QSize(50,50))
        trash_btn.setFixedSize(40,40)
        trash_btn.setStyleSheet("""
                                QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    }
                                QPushButton: hover {
                                    background-color:  #800000;
                                    border-radius: 18px;
                                }
                                """)
        
        trash_btn.clicked.connect(self.handle_delete_button)

        widget = QWidget()
        widget.setStyleSheet("background-color: #fcecec;")
        layout = QHBoxLayout(widget)
        layout.addWidget(trash_btn)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.table.setCellWidget(row, 3, widget)
        
    def delete_history_row(self, row):
        # Remove from file
        try:
            if os.path.exists(self.parent_window.history_file):
                with open(self.parent_window.history_file, 'r') as f:
                    history_data = json.load(f)
                if 0 <= row < len(history_data):
                    del history_data[row]
                    with open(self.parent_window.history_file, 'w') as f:
                        json.dump(history_data, f, indent=4)
                else:
                    QMessageBox.warning(self, "Error", "Row index out of range in history file.")
            self.table.removeRow(row)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not delete history item: {e}")

    def handle_delete_button(self):
        button = self.sender()
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 3)
            if cell_widget:
                btn = cell_widget.findChild(QPushButton)
                if btn == button:
                    self.delete_history_row(row)
                    break            
    def go_back(self):
        if self.parent_window:
            self.parent_window.welcome_panel()

def main():
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()