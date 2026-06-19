"""Qt stylesheet for Lupa — light editorial theme (petrol + amber on paper).

Deliberately distinct from the dark/purple look of its predecessor: a warm
"paper" surface, ink text, a petrol-teal primary and amber section accents.
"""

# Palette
#   paper bg    #f4f1ea   surface     #ffffff   inset      #faf7f0
#   ink         #1f2933   muted       #6b7280   border     #e4ddcf
#   petrol      #0f766e   petrol+     #0d9488   petrol-    #115e59
#   band        #103d3a   amber       #b5670a   terracotta #b4413c
#   selection   #cfe9e4

STYLE = """
QMainWindow {
    background-color: #f4f1ea;
}
QWidget {
    background-color: #f4f1ea;
    color: #1f2933;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10pt;
}

/* ---- Header band ---- */
QFrame#HeaderBand {
    background-color: #103d3a;
    border-radius: 16px;
}
QFrame#HeaderBand QLabel {
    background: transparent;
}
QLabel#Title {
    color: #f6f2e9;
    font-family: "Georgia", "Cambria", serif;
    font-size: 30pt;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 0;
}
QLabel#Subtitle {
    color: #9fc7c1;
    font-size: 10pt;
    padding: 0;
}
QLabel#SectionHeader {
    color: #b5670a;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 1px;
    padding-top: 6px;
}

/* ---- Card surface ---- */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e4ddcf;
    border-radius: 12px;
}

/* ---- Buttons ---- */
QPushButton {
    background-color: #ffffff;
    color: #1f2933;
    border: 1px solid #d9d2c2;
    border-radius: 9px;
    padding: 9px 16px;
    font-weight: 600;
    min-height: 18px;
}
QPushButton:hover {
    border-color: #0f766e;
    color: #0f766e;
}
QPushButton:pressed {
    background-color: #f0ece2;
}
QPushButton:disabled {
    background-color: #f0ece2;
    color: #b4ae9f;
    border-color: #e4ddcf;
}
QPushButton#PrimaryButton {
    background-color: #0f766e;
    color: #ffffff;
    border: none;
    padding: 10px 20px;
}
QPushButton#PrimaryButton:hover {
    background-color: #0d9488;
}
QPushButton#PrimaryButton:pressed {
    background-color: #115e59;
}
QPushButton#PrimaryButton:disabled {
    background-color: #cdd8d3;
    color: #fbfdfc;
}
QPushButton#DangerButton {
    background-color: #ffffff;
    color: #b4413c;
    border: 1px solid #e2b6b1;
}
QPushButton#DangerButton:hover {
    background-color: #b4413c;
    color: #ffffff;
    border-color: #b4413c;
}
QPushButton#GhostButton {
    background-color: transparent;
    color: #d8e7e3;
    border: 1px solid #2f5c58;
}
QPushButton#GhostButton:hover {
    background-color: #16504c;
    color: #f6f2e9;
    border-color: #4a716d;
}

/* ---- Lists & table ---- */
QListWidget, QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e4ddcf;
    border-radius: 12px;
    padding: 4px;
    selection-background-color: #cfe9e4;
    selection-color: #0f3d3a;
    alternate-background-color: #faf7f0;
    gridline-color: #ece6da;
}
QListWidget::item, QTableWidget::item {
    padding: 6px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background-color: #f0ece2;
}
QHeaderView::section {
    background-color: #e9f1ef;
    color: #0f766e;
    padding: 9px;
    border: none;
    border-right: 1px solid #ffffff;
    font-weight: 700;
}
QTableCornerButton::section {
    background-color: #e9f1ef;
    border: none;
}

/* ---- Progress ---- */
QProgressBar {
    background-color: #ece6da;
    border: none;
    border-radius: 7px;
    text-align: center;
    color: #1f2933;
    min-height: 22px;
    font-weight: 600;
}
QProgressBar::chunk {
    background-color: #0f766e;
    border-radius: 7px;
}

/* ---- Status bar ---- */
QStatusBar {
    background-color: #ece6da;
    color: #5c6670;
    border-top: 1px solid #ddd5c6;
}

/* ---- Checkboxes ---- */
QCheckBox {
    color: #3b454f;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #c8c0ae;
    border-radius: 5px;
    background-color: #ffffff;
}
QCheckBox::indicator:hover {
    border-color: #0f766e;
}
QCheckBox::indicator:checked {
    background-color: #0f766e;
    border-color: #0f766e;
}

/* ---- Drop zone ---- */
QFrame#DropZone {
    background-color: #faf7f0;
    border: 2px dashed #c8c0ae;
    border-radius: 14px;
    min-height: 96px;
}
QFrame#DropZone[active="true"] {
    border-color: #0f766e;
    background-color: #eef6f4;
}

/* ---- Text input ---- */
QPlainTextEdit {
    background-color: #ffffff;
    color: #1f2933;
    border: 1px solid #e4ddcf;
    border-radius: 10px;
    padding: 10px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 10pt;
    selection-background-color: #cfe9e4;
    selection-color: #0f3d3a;
}
QPlainTextEdit:focus {
    border-color: #0f766e;
}

/* ---- Scrollbars ---- */
QScrollBar:vertical {
    background: transparent;
    width: 11px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #cdc4b0;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #0f766e;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 11px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #cdc4b0;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #0f766e;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ---- Menu bar ---- */
QMenuBar {
    background-color: #f4f1ea;
    color: #3b454f;
    border-bottom: 1px solid #ddd5c6;
    padding: 3px;
}
QMenuBar::item {
    padding: 6px 12px;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background-color: #e9f1ef;
    color: #0f766e;
}
QMenu {
    background-color: #ffffff;
    color: #1f2933;
    border: 1px solid #e4ddcf;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 6px;
}
QMenu::item:selected {
    background-color: #e9f1ef;
    color: #0f766e;
}

/* ---- Splitter ---- */
QSplitter::handle {
    background: transparent;
}

/* ---- Tabbed research workspace ---- */
QFrame#AppHeader {
    background-color: #ffffff;
    border: none;
    border-bottom: 3px solid #0f766e;
    min-height: 52px;
    max-height: 52px;
}
QLabel#AppBrand {
    background: transparent;
    color: #103d3a;
    font-family: "Georgia", "Cambria", serif;
    font-size: 22pt;
    font-weight: 600;
}
QLabel#AppSubtitle {
    background: transparent;
    color: #5c6670;
    font-size: 10pt;
}
QLabel#HeaderContext {
    background: transparent;
    color: #b5670a;
    font-size: 8pt;
    font-weight: 700;
}
QFrame#HeaderSeparator {
    color: #ddd5c6;
    background-color: #ddd5c6;
    min-width: 1px;
    max-width: 1px;
    min-height: 28px;
}
QPushButton#HeaderIconButton,
QPushButton#InlineIconButton,
QPushButton#DangerIconButton {
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    padding: 0;
    border-radius: 6px;
}
QPushButton#DangerIconButton {
    color: #b4413c;
    border-color: #e2b6b1;
}
QTabWidget#WorkspaceTabs::pane {
    background-color: #f4f1ea;
    border: none;
    top: -1px;
}
QTabWidget#WorkspaceTabs QTabBar::tab {
    background-color: #ffffff;
    color: #5c6670;
    min-width: 150px;
    padding: 12px 22px 10px 22px;
    border: none;
    border-bottom: 3px solid #e4ddcf;
    font-size: 10pt;
    font-weight: 600;
}
QTabWidget#WorkspaceTabs QTabBar::tab:selected {
    color: #0f766e;
    border-bottom: 3px solid #0f766e;
}
QTabWidget#WorkspaceTabs QTabBar::tab:hover:!selected {
    color: #103d3a;
    background-color: #eef6f4;
}
QTabWidget#WorkspaceTabs QTabBar::tab:disabled {
    color: #b4ae9f;
    background-color: #faf7f0;
}
QFrame#WorkspacePanel {
    background-color: #ffffff;
    border: 1px solid #ddd5c6;
    border-radius: 6px;
}
QLabel#WorkspaceTitle {
    background: transparent;
    color: #103d3a;
    font-size: 12pt;
    font-weight: 700;
}
QLabel#FieldLabel {
    background: transparent;
    color: #b5670a;
    font-size: 8pt;
    font-weight: 700;
}
QLabel#MutedText {
    background: transparent;
    color: #6b7280;
    font-size: 9pt;
}
QFrame#ActionBar {
    background-color: #e9f1ef;
    border: 1px solid #cfe0dc;
    border-radius: 6px;
}
QFrame#SummaryBand {
    background-color: #103d3a;
    border: none;
    border-radius: 6px;
}
QFrame#SummaryBand QWidget,
QFrame#SummaryBand QLabel {
    background: transparent;
}
QLabel#SummaryCaption {
    color: #9fc7c1;
    font-size: 8pt;
    font-weight: 700;
}
QLabel#SummaryValue {
    color: #ffffff;
    font-size: 16pt;
    font-weight: 600;
}
QLabel#EmptyState {
    background-color: #ffffff;
    color: #8a8475;
    border: 1px dashed #c8c0ae;
    border-radius: 6px;
    font-size: 11pt;
}
QLabel#DropZoneLabel {
    background: transparent;
    color: #6b7280;
    font-size: 10pt;
}
QListWidget#CorpusFileList,
QTableWidget#ResultsTable {
    border-radius: 6px;
}
QComboBox {
    background-color: #ffffff;
    color: #1f2933;
    border: 1px solid #d9d2c2;
    border-radius: 6px;
    padding: 7px 10px;
    min-height: 18px;
}
QComboBox:focus {
    border-color: #0f766e;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QPushButton,
QPlainTextEdit,
QListWidget,
QTableWidget {
    border-radius: 6px;
}
"""
