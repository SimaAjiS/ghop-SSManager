from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Date, Boolean, BigInteger

metadata = MetaData()

# SQLite specific note:
# In SQLite, a column with type INTEGER PRIMARY KEY is an alias for the ROWID (except in WITHOUT ROWID tables)
# which is always a 64-bit signed integer.
# On the other hand, a column with type BIGINT PRIMARY KEY will be an auto-incrementing integer
# only if it is NOT an alias for the ROWID, but in SQLAlchemy, to get auto-increment behavior easily in SQLite,
# it is best to use Integer which maps to INTEGER.

# Table: MT_back_metal
mt_back_metal = Table(
    'MT_back_metal', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('back_metal_id', String),
    Column('back_metal', String),
    Column('back_metal_thickness_um', Float),
    Column('back_metal_anneal', String),
    Column('back_metal_display', String),
    Column('更新日', Date)
)

# Table: MT_barrier
mt_barrier = Table(
    'MT_barrier', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('barrier', String),
    Column('barrier_thickness_A', String),
    Column('barrier_display', String),
    Column('更新日', Date)
)

# Table: MT_device
# type is PK
mt_device = Table(
    'MT_device', metadata,
    Column('id', BigInteger), # Not PK, so BigInteger is fine, but if we want it to be auto-filled, it needs to be handled.
    # User said "id: BIGINT", but didn't say it's PK.
    # If it's not PK and not in Excel, it will be NULL.
    # If the requirement implies it should be a unique ID, we might need to generate it.
    # But let's stick to schema: id is just a column.
    Column('type', String, primary_key=True),
    Column('sheet_no', String),
    Column('barrier', String),
    Column('top_metal', String),
    Column('passivation', String),
    Column('wafer_thickness', BigInteger),
    Column('back_metal', String),
    Column('status', String),
    Column('更新日', Date)
)

# Table: MT_elec_characteristic
mt_elec_characteristic = Table(
    'MT_elec_characteristic', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sheet_no', String),
    Column('item', String),
    Column('+/-', Boolean), # New column
    Column('min', Float),
    Column('typ', Float),
    Column('max', Float),
    Column('unit', String),
    Column('bias_vgs', String),
    Column('bias_igs', String),
    Column('bias_vds', String),
    Column('bias_ids', String),
    Column('bias_vss', String),
    Column('bias_iss', String),
    Column('cond', String),
    Column('更新日', Date)
)

# Table: MT_esd
mt_esd = Table(
    'MT_esd', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('esd_V', BigInteger),
    Column('description', String),
    Column('esd_display', String),
    Column('更新日', Date)
)

# Table: MT_item
mt_item = Table(
    'MT_item', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('item', String),
    Column('更新日', Date)
)

# Table: MT_maskset
mt_maskset = Table(
    'MT_maskset', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('maskset', String),
    Column('level', String),
    Column('chip_x_mm', Float),
    Column('chip_y_mm', Float),
    Column('dicing_line_um', Integer),
    Column('pdpw', Integer),
    Column('appearance', String),
    Column('pad_x_gate_um', Integer),
    Column('pad_y_gate_um', Integer),
    Column('pad_x_source_um', Integer),
    Column('pad_y_source_um', Integer),
    Column('更新日', Date)
)

# Table: MT_passivation
mt_passivation = Table(
    'MT_passivation', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('passivation_type', String),
    Column('passivation_thickness_A', BigInteger),
    Column('passivation_display', String),
    Column('更新日', Date)
)

# Table: MT_spec_sheet
# sheet_no is PK
mt_spec_sheet = Table(
    'MT_spec_sheet', metadata,
    Column('id', BigInteger),
    Column('sheet_no', String, primary_key=True),
    Column('sheet_name', String),
    Column('sheet_revision', Integer),
    Column('vdss_V', Integer),
    Column('vgss_V', Integer),
    Column('idss_A', Integer),
    Column('esd_display', String),
    Column('maskset', String),
    Column('更新日', Date)
)

# Table: MT_status
mt_status = Table(
    'MT_status', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('status', String),
    Column('更新日', Date)
)

# Table: MT_top_metal
mt_top_metal = Table(
    'MT_top_metal', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('top_metal', String),
    Column('top_metal_thickness_um', Float),
    Column('top_metal_display', String),
    Column('更新日', Date)
)

# Table: MT_unit
mt_unit = Table(
    'MT_unit', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('unit_category', String),
    Column('SI_prefix', String),
    Column('unit_display', String),
    Column('更新日', Date)
)

# Table: MT_wafer_thickness
mt_wafer_thickness = Table(
    'MT_wafer_thickness', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('wafer_thickness_um', BigInteger),
    Column('wafer_thickness_tolerance_um', BigInteger),
    Column('wafer_thickness_display', String),
    Column('更新日', Date)
)
