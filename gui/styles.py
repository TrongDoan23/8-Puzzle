LIGHT_PALETTE = {
    "bg_main":            "#F0F4F8",
    "bg_panel":           "#FFFFFF",
    "bg_board":           "#E2EAF4",
    "tile_bg":            "#4A90D9",
    "tile_bg_hover":      "#357ABD",
    "tile_text":          "#FFFFFF",
    "blank_bg":           "#CDD6E3",
    "border":             "#D0D8E4",
    "text_primary":       "#1A2332",
    "text_secondary":     "#6B7A90",
    "btn_primary":        "#4A90D9",
    "btn_primary_hover":  "#357ABD",
    "btn_primary_press":  "#2A6099",
    "btn_danger":         "#E05555",
    "btn_danger_hover":   "#C44444",
    "btn_success":        "#44B87A",
    "btn_success_hover":  "#359960",
    "btn_warning":        "#F5A623",
    "btn_warning_hover":  "#E09510",
    "btn_neutral":        "#8090A4",
    "btn_neutral_hover":  "#6B7A8E",
    "accent":             "#4A90D9",
    "stats_bg":           "#F7FAFC",
    "step_selected":      "#D6EAFF",
    "step_hover":         "#EBF4FF",
    "groupbox_title_bg":  "#FFFFFF",
    "scrollbar_handle":   "#C5CDD8",
}

DARK_PALETTE = {
    "bg_main":            "#1A2332",
    "bg_panel":           "#243040",
    "bg_board":           "#1E2A3A",
    "tile_bg":            "#3A78C4",
    "tile_bg_hover":      "#4A90D9",
    "tile_text":          "#F0F4F8",
    "blank_bg":           "#2A3A50",
    "border":             "#354A60",
    "text_primary":       "#E8EDF2",
    "text_secondary":     "#8A9BB0",
    "btn_primary":        "#3A78C4",
    "btn_primary_hover":  "#4A90D9",
    "btn_primary_press":  "#2A6099",
    "btn_danger":         "#C44444",
    "btn_danger_hover":   "#E05555",
    "btn_success":        "#359960",
    "btn_success_hover":  "#44B87A",
    "btn_warning":        "#D4911F",
    "btn_warning_hover":  "#F5A623",
    "btn_neutral":        "#3A4A60",
    "btn_neutral_hover":  "#4A5A70",
    "accent":             "#4A90D9",
    "stats_bg":           "#1E2A3A",
    "step_selected":      "#1E3A5A",
    "step_hover":         "#243040",
    "groupbox_title_bg":  "#243040",
    "scrollbar_handle":   "#354A60",
}


def get_stylesheet(p: dict) -> str:
    return f"""
/* ── Base ─────────────────────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {p['bg_main']};
    color: {p['text_primary']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}}

/* ── Named panels ──────────────────────────────────────────────────── */
QWidget#left_panel {{
    background-color: {p['bg_panel']};
    border-radius: 12px;
    border: 1px solid {p['border']};
}}
QWidget#right_panel {{
    background-color: {p['bg_panel']};
    border-radius: 12px;
    border: 1px solid {p['border']};
}}

/* ── ScrollArea for right panel ────────────────────────────────────── */
QScrollArea#right_scroll {{
    background-color: transparent;
    border: none;
}}
QScrollArea#right_scroll > QWidget > QWidget {{
    background-color: transparent;
}}

/* ── Labels ───────────────────────────────────────────────────────── */
QLabel {{
    color: {p['text_primary']};
    background-color: transparent;
}}
QLabel#section_title {{
    font-size: 15px;
    font-weight: 700;
    color: {p['text_primary']};
}}
QLabel#subtitle {{
    font-size: 11px;
    color: {p['text_secondary']};
}}
QLabel#stat_label {{
    font-size: 11px;
    color: {p['text_secondary']};
}}
QLabel#stat_value {{
    font-size: 12px;
    font-weight: 600;
    color: {p['accent']};
}}

/* ── GroupBox ─────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1.5px solid {p['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 6px;
    font-size: 12px;
    font-weight: 600;
    color: {p['text_primary']};
    background-color: transparent;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 0px;
    padding: 0 6px;
    background-color: {p['groupbox_title_bg']};
    color: {p['text_primary']};
}}

/* ── Buttons ──────────────────────────────────────────────────────── */
QPushButton {{
    border-radius: 7px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    border: none;
    min-height: 34px;
    color: #FFFFFF;
}}

QPushButton#btn_random {{
    background-color: {p['btn_neutral']};
}}
QPushButton#btn_random:hover {{
    background-color: {p['btn_neutral_hover']};
}}
QPushButton#btn_random:pressed {{
    background-color: {p['btn_primary_press']};
}}

QPushButton#btn_solve {{
    background-color: {p['btn_primary']};
}}
QPushButton#btn_solve:hover {{
    background-color: {p['btn_primary_hover']};
}}
QPushButton#btn_solve:pressed {{
    background-color: {p['btn_primary_press']};
}}

QPushButton#btn_pause {{
    background-color: {p['btn_warning']};
}}
QPushButton#btn_pause:hover {{
    background-color: {p['btn_warning_hover']};
}}

QPushButton#btn_continue {{
    background-color: {p['btn_success']};
}}
QPushButton#btn_continue:hover {{
    background-color: {p['btn_success_hover']};
}}

QPushButton#btn_stop {{
    background-color: {p['btn_danger']};
}}
QPushButton#btn_stop:hover {{
    background-color: {p['btn_danger_hover']};
}}

QPushButton#btn_reset {{
    background-color: {p['btn_neutral']};
}}
QPushButton#btn_reset:hover {{
    background-color: {p['btn_neutral_hover']};
}}

QPushButton:disabled {{
    background-color: {p['border']};
    color: {p['text_secondary']};
    opacity: 0.6;
}}

/* ── ComboBox ─────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {p['bg_main']};
    color: {p['text_primary']};
    border: 1.5px solid {p['border']};
    border-radius: 7px;
    padding: 5px 10px;
    font-size: 12px;
    min-height: 30px;
    selection-background-color: {p['accent']};
}}
QComboBox:hover {{
    border-color: {p['accent']};
}}
QComboBox:focus {{
    border-color: {p['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {p['bg_panel']};
    color: {p['text_primary']};
    border: 1.5px solid {p['border']};
    border-radius: 6px;
    selection-background-color: {p['accent']};
    selection-color: #FFFFFF;
    padding: 4px;
    outline: none;
}}

/* ── Slider ───────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 5px;
    background: {p['border']};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {p['accent']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {p['btn_primary_hover']};
}}
QSlider::sub-page:horizontal {{
    background: {p['accent']};
    border-radius: 3px;
}}

/* ── ScrollBars ───────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {p['bg_main']};
    width: 7px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {p['scrollbar_handle']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['accent']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ── Stats panel ──────────────────────────────────────────────────── */
QWidget#stats_panel {{
    background-color: {p['stats_bg']};
    border-radius: 8px;
    border: 1px solid {p['border']};
}}

/* ── Solution list ────────────────────────────────────────────────── */
QListWidget {{
    background-color: {p['bg_main']};
    border: 1.5px solid {p['border']};
    border-radius: 8px;
    color: {p['text_primary']};
    font-size: 12px;
    outline: none;
}}
QListWidget::item {{
    padding: 5px 10px;
    border-bottom: 1px solid {p['border']};
}}
QListWidget::item:selected {{
    background-color: {p['step_selected']};
    color: {p['accent']};
    border-left: 3px solid {p['accent']};
}}
QListWidget::item:hover:!selected {{
    background-color: {p['step_hover']};
}}

/* ── Separator ────────────────────────────────────────────────────── */
QFrame#separator {{
    background-color: {p['border']};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

/* ── Status bar ───────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {p['bg_panel']};
    color: {p['text_secondary']};
    border-top: 1px solid {p['border']};
    font-size: 11px;
}}
QStatusBar QLabel {{
    color: {p['text_secondary']};
}}

/* ── MessageBox ───────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {p['bg_panel']};
    color: {p['text_primary']};
}}
QMessageBox QLabel {{
    color: {p['text_primary']};
}}
QMessageBox QPushButton {{
    background-color: {p['btn_primary']};
    min-width: 80px;
}}
    """
