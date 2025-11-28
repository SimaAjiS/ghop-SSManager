from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MT_BackMetal(BaseModel):
    back_metal_id: Optional[str] = None
    back_metal: Optional[str] = None
    back_metal_thickness_um: Optional[float] = None
    back_metal_anneal: Optional[str] = None
    back_metal_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_Barrier(BaseModel):
    barrier: Optional[str] = None
    barrier_thickness_A: Optional[str] = None
    barrier_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_Device(BaseModel):
    type: str  # PK
    sheet_no: Optional[str] = None
    barrier: Optional[str] = None
    top_metal: Optional[str] = None
    passivation: Optional[str] = None
    wafer_thickness: Optional[str] = None
    back_metal: Optional[str] = None
    status: Optional[str] = None
    更新日: Optional[date] = None


class MT_ElecCharacteristic(BaseModel):
    sheet_no: Optional[str] = None
    item: Optional[str] = None
    plus_minus: Optional[bool] = Field(alias="+/-", default=None)
    min: Optional[float] = None
    typ: Optional[float] = None
    max: Optional[float] = None
    unit: Optional[str] = None
    bias_vgs: Optional[str] = None
    bias_igs: Optional[str] = None
    bias_vds: Optional[str] = None
    bias_ids: Optional[str] = None
    bias_vss: Optional[str] = None
    bias_iss: Optional[str] = None
    cond: Optional[str] = None
    更新日: Optional[date] = None


class MT_Esd(BaseModel):
    esd_V: Optional[int] = None
    description: Optional[str] = None
    esd_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_Item(BaseModel):
    item: Optional[str] = None
    更新日: Optional[date] = None


class MT_Maskset(BaseModel):
    maskset: Optional[str] = None
    level: Optional[str] = None
    chip_x_mm: Optional[float] = None
    chip_y_mm: Optional[float] = None
    dicing_line_um: Optional[int] = None
    pdpw: Optional[str] = None
    appearance: Optional[str] = None
    pad_x_gate_um: Optional[int] = None
    pad_y_gate_um: Optional[int] = None
    pad_x_source_um: Optional[int] = None
    pad_y_source_um: Optional[int] = None
    更新日: Optional[date] = None


class MT_Passivation(BaseModel):
    passivation_type: Optional[str] = None
    passivation_thickness_A: Optional[int] = None
    passivation_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_SpecSheet(BaseModel):
    sheet_no: str  # PK
    sheet_name: Optional[str] = None
    sheet_revision: Optional[int] = None
    vdss_V: Optional[int] = None
    vgss_V: Optional[int] = None
    idss_A: Optional[int] = None
    esd_display: Optional[str] = None
    maskset: Optional[str] = None
    更新日: Optional[date] = None


class MT_Status(BaseModel):
    status: Optional[str] = None
    更新日: Optional[date] = None


class MT_TopMetal(BaseModel):
    top_metal: Optional[str] = None
    top_metal_thickness_um: Optional[float] = None
    top_metal_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_Unit(BaseModel):
    unit_category: Optional[str] = None
    SI_prefix: Optional[str] = None
    unit_display: Optional[str] = None
    更新日: Optional[date] = None


class MT_WaferThickness(BaseModel):
    wafer_thickness_um: Optional[int] = None
    wafer_thickness_tolerance_um: Optional[int] = None
    wafer_thickness_display: Optional[str] = None
    更新日: Optional[date] = None
