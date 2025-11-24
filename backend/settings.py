import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Source Configuration
# The Excel file containing master tables
DATA_DIR = os.path.join(BASE_DIR, "data")
# MASTER_EXCEL_FILE = os.path.join(DATA_DIR, "master_tables_dummy.xlsx")
MASTER_EXCEL_FILE = os.path.join(DATA_DIR, "master_tables_template.xlsx")


# Database Configuration
DB_NAME = "master.db"
DB_FILE = os.path.join(BASE_DIR, DB_NAME)
DB_URL = f"sqlite:///{DB_FILE}"

# Table Display Order
TABLE_ORDER = [
    "MT_spec_sheet",
    "MT_device",
    "MT_elec_characteristic",
    "MT_item",
    "MT_unit",
    "MT_maskset",
    "MT_top_metal",
    "MT_barrier",
    "MT_passivation",
    "MT_wafer_thickness",
    "MT_back_metal",
    "MT_status",
]
