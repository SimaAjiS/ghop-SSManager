from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Base directory of the backend
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    # Data Source Configuration
    # The Excel file containing master tables
    STORAGE_DIR: Path = BASE_DIR / "storage"
    DATA_DIR: Path = STORAGE_DIR  # storage/ 直下にすべてのデータファイルを配置

    # Master Excel file configuration
    # Priority: MASTER_EXCEL_FILE > NETWORK_MASTER_DIR > LOCAL_MASTER_EXCEL_FILE
    MASTER_EXCEL_FILE: str | None = None
    NETWORK_MASTER_DIR: str | None = None

    # Database Configuration
    DB_NAME: str = "master.db"
    DB_FILE: Path = STORAGE_DIR / DB_NAME
    DB_URL: str = f"sqlite:///{STORAGE_DIR / DB_NAME}"

    # Table Display Order
    TABLE_ORDER: list[str] = [
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

    @property
    def local_master_excel_file(self) -> Path:
        """Local master Excel file path."""
        return self.DATA_DIR / "master_tables.xlsx"

    @property
    def network_master_excel_file(self) -> Path | None:
        """Network master Excel file path if NETWORK_MASTER_DIR is set."""
        if self.NETWORK_MASTER_DIR:
            return Path(self.NETWORK_MASTER_DIR) / "master_tables.xlsx"
        return None

    @property
    def resolved_master_excel_file(self) -> Path:
        """
        Resolved master Excel file path.
        Priority: MASTER_EXCEL_FILE > NETWORK_MASTER_DIR > LOCAL_MASTER_EXCEL_FILE
        """
        if self.MASTER_EXCEL_FILE:
            return Path(self.MASTER_EXCEL_FILE)

        network_file = self.network_master_excel_file
        if network_file and network_file.exists():
            return network_file

        return self.local_master_excel_file


# Create a singleton instance
settings = Settings()

# Backward compatibility: Export as module-level constants
BASE_DIR = settings.BASE_DIR
DATA_DIR = settings.DATA_DIR
STORAGE_DIR = settings.STORAGE_DIR
LOCAL_MASTER_EXCEL_FILE = str(settings.local_master_excel_file)
NETWORK_MASTER_EXCEL_FILE = (
    str(settings.network_master_excel_file)
    if settings.network_master_excel_file
    else None
)
MASTER_EXCEL_FILE = str(settings.resolved_master_excel_file)
DB_NAME = settings.DB_NAME
DB_FILE = settings.DB_FILE
DB_URL = settings.DB_URL
TABLE_ORDER = settings.TABLE_ORDER
