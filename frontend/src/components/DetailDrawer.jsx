import React, { useState, useEffect } from "react";
import {
  X,
  Printer,
  FileSpreadsheet,
  Edit3,
  Save,
  RotateCcw,
  Plus,
  Trash2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { buildApiUrl } from "../lib/api";

const DEVICE_EDITABLE_FIELDS = [
  "sheet_no",
  "status",
  "barrier",
  "passivation",
  "top_metal",
  "wafer_thickness",
  "back_metal",
];

const SPEC_EDITABLE_FIELDS = [
  "sheet_name",
  "sheet_revision",
  "vdss_V",
  "vgss_V",
  "idss_A",
  "esd_display",
];

const defaultCharacteristic = () => ({
  item: "",
  min: "",
  typ: "",
  max: "",
  unit: "",
  bias_vgs: "",
  bias_igs: "",
  bias_vds: "",
  bias_ids: "",
  bias_vss: "",
  bias_iss: "",
  cond: "",
});

const DetailDrawer = ({
  isOpen,
  onClose,
  title,
  data,
  editable = false,
  onSave,
  onDirtyChange,
  isLoading = false,
  errorMessage,
}) => {
  const [isEditMode, setIsEditMode] = useState(false);
  const [deviceForm, setDeviceForm] = useState({});
  const [specSheetForm, setSpecSheetForm] = useState({});
  const [characteristicsForm, setCharacteristicsForm] = useState([]);
  const [saving, setSaving] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [isDirty, setIsDirty] = useState(false);

  const device = data?.device;
  const characteristics = data?.characteristics || [];

  const handlePrint = () => {
    if (!device) return;
    const originalTitle = document.title;
    const sheetNo = getVal(device, "sheet_no");
    const sheetName = getVal(device, "sheet_name");
    document.title = `${sheetNo}_${sheetName}`;
    window.print();
    document.title = originalTitle;
  };

  const handleExport = async () => {
    if (!device) return;

    try {
      const deviceType = device.type;
      const encodedType = encodeURIComponent(deviceType);
      const response = await fetch(
        buildApiUrl(`/api/devices/${encodedType}/export-excel`)
      );

      if (!response.ok) {
        throw new Error("Export failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = `SpecSheet_${deviceType}.xlsx`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch && filenameMatch.length === 2)
          filename = filenameMatch[1];
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Export error:", error);
      alert("Failed to export Excel file.");
    }
  };

  const formatCondition = (char) => {
    const parts = [];
    if (char.bias_vgs) parts.push(`VGS=${char.bias_vgs}`);
    if (char.bias_igs) parts.push(`IGS=${char.bias_igs}`);
    if (char.bias_vds) parts.push(`VDS=${char.bias_vds}`);
    if (char.bias_ids) parts.push(`IDS=${char.bias_ids}`);
    if (char.bias_vss) parts.push(`VSS=${char.bias_vss}`);
    if (char.bias_iss) parts.push(`ISS=${char.bias_iss}`);
    if (char.cond) parts.push(char.cond);

    return parts.join(", ");
  };

  const getVal = (obj, key, defaultVal = "-") => {
    return obj && obj[key] !== undefined && obj[key] !== null
      ? obj[key]
      : defaultVal;
  };

  const formatLimitValue = (val, item) => {
    if (val === undefined || val === null || val === "") return "";
    if (item === "IGSS" || item === "VGSS") {
      return `+/- ${val}`;
    }
    return val;
  };

  const pickFields = (source, fields) => {
    if (!source) return {};
    return fields.reduce((acc, field) => {
      acc[field] = source[field] ?? "";
      return acc;
    }, {});
  };

  const markDirty = () => {
    if (!isDirty) {
      setIsDirty(true);
      onDirtyChange?.(true);
    }
  };

  const resetDirty = () => {
    setIsDirty(false);
    onDirtyChange?.(false);
  };

  const initializeForms = () => {
    if (!device) return;
    setDeviceForm(pickFields(device, DEVICE_EDITABLE_FIELDS));
    setSpecSheetForm(pickFields(device, SPEC_EDITABLE_FIELDS));
    setCharacteristicsForm(characteristics.map((char) => ({ ...char })));
    resetDirty();
  };

  useEffect(() => {
    if (!isEditMode) {
      initializeForms();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [device, characteristics, isEditMode]);

  useEffect(() => {
    if (!isOpen) {
      setIsEditMode(false);
      setDeviceForm({});
      setSpecSheetForm({});
      setCharacteristicsForm([]);
      resetDirty();
      setLocalError(null);
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleFieldChange = (section, field, value) => {
    markDirty();
    if (section === "device") {
      setDeviceForm((prev) => ({ ...prev, [field]: value }));
    } else {
      setSpecSheetForm((prev) => ({ ...prev, [field]: value }));
    }
  };

  const handleCharacteristicChange = (index, field, value) => {
    markDirty();
    setCharacteristicsForm((prev) =>
      prev.map((row, idx) =>
        idx === index
          ? {
              ...row,
              [field]: value,
            }
          : row
      )
    );
  };

  const handleAddCharacteristic = () => {
    markDirty();
    setCharacteristicsForm((prev) => [...prev, defaultCharacteristic()]);
  };

  const handleRemoveCharacteristic = (index) => {
    markDirty();
    setCharacteristicsForm((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleStartEdit = () => {
    setIsEditMode(true);
    initializeForms();
    setLocalError(null);
  };

  const handleCancelEdit = () => {
    if (
      isDirty &&
      !window.confirm("保存されていない変更があります。破棄しますか？")
    ) {
      return;
    }
    initializeForms();
    setIsEditMode(false);
    setLocalError(null);
  };

  const handleSave = async () => {
    if (!onSave || !device) return;
    setSaving(true);
    setLocalError(null);
    try {
      await onSave({
        device: deviceForm,
        spec_sheet: specSheetForm,
        characteristics: characteristicsForm,
      });
      setIsEditMode(false);
      resetDirty();
    } catch (err) {
      setLocalError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  const combinedError = errorMessage || localError;
  const canEdit = editable && device;

  const renderTextValue = (field, section = "device", fallback = "-") => {
    const isEditableField =
      canEdit &&
      isEditMode &&
      (section === "device"
        ? DEVICE_EDITABLE_FIELDS.includes(field)
        : SPEC_EDITABLE_FIELDS.includes(field));

    if (!isEditableField) {
      return getVal(device, field, fallback);
    }

    const reference = device?.[field];
    const inputType = typeof reference === "number" ? "number" : "text";
    const value =
      section === "device" ? deviceForm[field] ?? "" : specSheetForm[field] ?? "";

    return (
      <input
        type={inputType}
        step="any"
        className="drawer-input"
        value={value}
        onChange={(event) =>
          handleFieldChange(section, field, event.target.value)
        }
      />
    );
  };

  return (
    <>
      <div
        className={`drawer-backdrop ${isOpen ? "open" : ""}`}
        onClick={onClose}
      />

      <div
        className={`drawer-panel ${isOpen ? "open" : ""}`}
        style={{ width: "900px", maxWidth: "95vw" }}
      >
        <div
          className="drawer-header"
          style={{ borderBottom: "none", paddingBottom: 0 }}
        >
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            {canEdit && !isEditMode && (
              <button
                onClick={handleStartEdit}
                className="btn btn-ghost"
                title="Edit"
              >
                <Edit3 size={20} />
                編集
              </button>
            )}
            {canEdit && isEditMode && (
              <>
                <button
                  onClick={handleSave}
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <Loader2 size={18} className="spin" />
                      保存中...
                    </>
                  ) : (
                    <>
                      <Save size={18} />
                      保存
                    </>
                  )}
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="btn btn-secondary"
                  disabled={saving}
                >
                  <RotateCcw size={18} />
                  キャンセル
                </button>
              </>
            )}
            <button onClick={handlePrint} className="btn btn-ghost" title="Print">
              <Printer size={20} />
            </button>
            <button
              onClick={handleExport}
              className="btn btn-ghost"
              title="Export Excel"
            >
              <FileSpreadsheet size={20} />
            </button>
            <button onClick={onClose} className="btn btn-ghost">
              <X size={24} />
            </button>
          </div>
        </div>

        <div
          className="drawer-content"
          style={{ padding: "2rem", background: "white", color: "black" }}
        >
        {(title || device?.type) && (
          <h2 style={{ marginTop: 0 }}>
            {title || device?.type || "Device Details"}
          </h2>
        )}
          {combinedError && (
            <div className="error" style={{ marginBottom: "1rem" }}>
              <AlertCircle size={20} style={{ marginRight: "0.5rem" }} />
              {combinedError}
            </div>
          )}
          {(!data || isLoading) && (
            <div style={{ padding: "2rem", textAlign: "center" }}>
              <Loader2 className="spin" style={{ marginBottom: "0.5rem" }} />
              Loading details...
            </div>
          )}
          {!isLoading && data?.error && (
            <div
              style={{ padding: "2rem", textAlign: "center", color: "red" }}
            >
              {data.error}
            </div>
          )}
          {!isLoading && data && !data.error && (
            <div className="spec-sheet">
              <div className="spec-header-table">
                <div className="spec-header-title">
                  <h1>SPEC SHEET (FOR REFERENCE)</h1>
                </div>
                <div className="spec-header-sheet">
                  <div className="header-label">SHEET No.</div>
                  <div className="header-value">
                    {renderTextValue("sheet_no", "device")}
                  </div>
                </div>
                <div className="spec-header-rev">
                  <div className="header-label">Rev.</div>
                  <div className="header-value">
                    {renderTextValue("sheet_revision", "spec", "-")}
                  </div>
                </div>
                <div className="spec-header-page">
                  <div className="header-label">Page.</div>
                  <div className="header-value">1 of 1</div>
                </div>
              </div>

              <div className="spec-row type-row">
                <span className="label">
                  TYPE: {renderTextValue("sheet_name", "spec")}
                </span>
              </div>

              <div className="chip-info-grid">
                <div className="chip-appearance">
                  <div className="section-label">CHIP APPEARANCE</div>
                  <div className="appearance-placeholder">
                    {device?.appearance ? (
                      <>
                        <img
                          src={buildApiUrl(
                            `/static/chip_appearances/${device.appearance}`
                          )}
                          alt="Chip Appearance"
                          style={{
                            maxWidth: "100%",
                            maxHeight: "200px",
                            objectFit: "contain",
                          }}
                          onError={(e) => {
                            // eslint-disable-next-line no-param-reassign
                            e.target.style.display = "none";
                            e.target.nextSibling.style.display = "flex";
                          }}
                        />
                        <div
                          style={{
                            width: "100px",
                            height: "140px",
                            background: "#ddd",
                            display: "none",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "#666",
                          }}
                        >
                          No Image
                        </div>
                      </>
                    ) : (
                      <div
                        style={{
                          width: "100px",
                          height: "140px",
                          background: "#ddd",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: "#666",
                        }}
                      >
                        No Image
                      </div>
                    )}
                  </div>
                </div>
                <div className="chip-specs">
                  <div className="spec-item">
                    <span className="label">CHIP SIZE</span>
                    <span className="value">
                      {getVal(device, "chip_x_mm")} * {getVal(device, "chip_y_mm")}{" "}
                      mm
                    </span>
                  </div>
                  <div className="spec-item">
                    <span className="label">CHIP THICKNESS</span>
                    <span className="value">Refer to "NOTE"</span>
                  </div>
                  <div className="spec-item double-height">
                    <span className="label">BONDING PAD DIMENSIONS</span>
                    <div className="sub-specs">
                      <div className="sub-spec">
                        <span className="sub-label">GATE</span>
                        <span className="sub-value">
                          {getVal(device, "pad_x_gate_um")} *{" "}
                          {getVal(device, "pad_y_gate_um")} um
                        </span>
                      </div>
                      <div className="sub-spec">
                        <span className="sub-label">SOURCE</span>
                        <span className="sub-value">
                          {getVal(device, "pad_x_source_um")} *{" "}
                          {getVal(device, "pad_y_source_um")} um
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="spec-item">
                    <span className="label">SCRIBE LINE WIDTH</span>
                    <span className="value">
                      {getVal(device, "dicing_line_um")} um
                    </span>
                  </div>
                  <div className="spec-item">
                    <span className="label">TOP METAL</span>
                    <span className="value">Refer to "NOTE"</span>
                  </div>
                  <div className="spec-item">
                    <span className="label">BACK METAL</span>
                    <span className="value">Refer to "NOTE"</span>
                  </div>
                  <div className="spec-item">
                    <span className="label">WAFER SIZE</span>
                    <span className="value">6inch</span>
                  </div>
                  <div className="spec-item">
                    <span className="label">POSSIBLE DIE PER WAFER</span>
                    <span className="value">{getVal(device, "pdpw")}pcs</span>
                  </div>
                </div>
              </div>

              <div className="section-header">
                Maximum Ratings(Ta=25C) (FOR REFERENCE)
              </div>
              <table className="spec-table ratings-table">
                <thead>
                  <tr>
                    <th>Characteristics</th>
                    <th>Symbol</th>
                    <th>Ratings</th>
                    <th>Unit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Drain-Source Voltage</td>
                    <td>VDSS</td>
                    <td>{renderTextValue("vdss_V", "spec")}</td>
                    <td>V</td>
                  </tr>
                  <tr>
                    <td>Gate-Source Voltage</td>
                    <td>VGSS</td>
                    <td>+/- {renderTextValue("vgss_V", "spec")}</td>
                    <td>V</td>
                  </tr>
                </tbody>
              </table>

              <div className="section-header">WAFER PROBING SPEC (Ta=25C)</div>
              <table className="spec-table probing-table">
                <thead>
                  <tr>
                    <th rowSpan="2">No</th>
                    <th rowSpan="2">MODE</th>
                    <th colSpan="3">LIMIT</th>
                    <th rowSpan="2">UNIT</th>
                    <th rowSpan="2">CONDITIONS</th>
                    {isEditMode && <th rowSpan="2">操作</th>}
                  </tr>
                  <tr>
                    <th>MIN.</th>
                    <th>Typ</th>
                    <th>MAX.</th>
                  </tr>
                </thead>
                <tbody>
                  {(isEditMode ? characteristicsForm : characteristics).map(
                    (char, index) => (
                      <tr key={`char-${index}`}>
                        <td>{index + 1}</td>
                        <td style={{ textAlign: "left", paddingLeft: "1rem" }}>
                          {isEditMode ? (
                            <input
                              className="drawer-input"
                              value={char.item ?? ""}
                              onChange={(event) =>
                                handleCharacteristicChange(
                                  index,
                                  "item",
                                  event.target.value
                                )
                              }
                            />
                          ) : (
                            char.item
                          )}
                        </td>
                        {["min", "typ", "max"].map((field) => (
                          <td key={`${field}-${index}`}>
                            {isEditMode ? (
                              <input
                                className="drawer-input"
                                value={char[field] ?? ""}
                                onChange={(event) =>
                                  handleCharacteristicChange(
                                    index,
                                    field,
                                    event.target.value
                                  )
                                }
                              />
                            ) : (
                              formatLimitValue(
                                getVal(char, field, ""),
                                char.item
                              )
                            )}
                          </td>
                        ))}
                        <td>
                          {isEditMode ? (
                            <input
                              className="drawer-input"
                              value={char.unit ?? ""}
                              onChange={(event) =>
                                handleCharacteristicChange(
                                  index,
                                  "unit",
                                  event.target.value
                                )
                              }
                            />
                          ) : (
                            char.unit
                          )}
                        </td>
                        <td style={{ textAlign: "left", paddingLeft: "1rem" }}>
                          {isEditMode ? (
                            <textarea
                              className="drawer-input"
                              value={char.cond ?? ""}
                              onChange={(event) =>
                                handleCharacteristicChange(
                                  index,
                                  "cond",
                                  event.target.value
                                )
                              }
                            />
                          ) : (
                            formatCondition(char)
                          )}
                        </td>
                        {isEditMode && (
                          <td>
                            <button
                              type="button"
                              className="btn btn-ghost btn-icon"
                              onClick={() => handleRemoveCharacteristic(index)}
                            >
                              <Trash2 size={16} />
                            </button>
                          </td>
                        )}
                      </tr>
                    )
                  )}
                  {isEditMode && (
                    <tr>
                      <td colSpan={7} style={{ textAlign: "left" }}>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={handleAddCharacteristic}
                        >
                          <Plus size={16} />
                          行を追加
                        </button>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
              <div className="note-text">
                The F/T specifications must be relaxed than the wafer probing
                specifications
              </div>
              <div className="note-text">
                *{renderTextValue("esd_display", "spec", "")}
              </div>

              <div className="notes-section">
                <div className="note-row">
                  <span className="note-label">Sample probe</span>
                  <span className="note-content">
                    400dice or over / wafer for all wafers.
                  </span>
                </div>
                <div className="note-row">
                  <span className="note-label">Probing</span>
                  <span className="note-content">
                    100% probing is not allowed. The wafers shall be sample
                    probed in order to guarantee the minimum yield.
                  </span>
                </div>
                <div className="note-row">
                  <span className="note-label">Inking</span>
                  <span className="note-content">
                    Marking will be made for those areas of wafer cramp nail and
                    process control monitor.
                  </span>
                </div>
                <div className="note-row">
                  <span className="note-label">Ink type</span>
                  <span className="note-content">Black ink of Epoxy type.</span>
                </div>
              </div>

              <div className="section-header">NOTE:</div>
              <table className="spec-table footer-table">
                <thead>
                  <tr>
                    <th>TYPE: {getVal(device, "sheet_name")}</th>
                    <th>TOP METAL</th>
                    <th>CHIP THICKNESS</th>
                    <th>BACK METAL</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.related_devices || []).map(
                    (deviceItem, index) => (
                      <tr key={`related-${index}`}>
                        <td>{deviceItem.type}</td>
                        <td>{deviceItem.top_metal_display || "-"}</td>
                        <td>{deviceItem.wafer_thickness_display || "-"}</td>
                        <td>{deviceItem.back_metal_display || "-"}</td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
              <div
                className="footer-date"
                style={{ textAlign: "right", marginTop: "0.5rem" }}
              >
                {new Date().toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default DetailDrawer;
