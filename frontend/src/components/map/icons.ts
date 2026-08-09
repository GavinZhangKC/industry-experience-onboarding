import L from "leaflet";

// Plain divIcon markers instead of Leaflet's default image icon, which needs
// asset-path patching under most bundlers. Each icon carries a white halo so
// it reads against any tile colour underneath.
function pinIcon(label: string, background: string, textColor = "#ffffff"): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="
        width: 28px; height: 28px; border-radius: 50%;
        background: ${background}; color: ${textColor};
        border: 2px solid #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.4);
        display: flex; align-items: center; justify-content: center;
        font-family: system-ui, sans-serif; font-weight: 700; font-size: 13px;
      ">${label}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

export const originIcon = pinIcon("A", "#2f6b63");
export const destinationIcon = pinIcon("B", "#2f6b63");
export const quietSpaceIcon = pinIcon("Q", "#3e6b9b");
export const quietSpaceSelectedIcon = pinIcon("Q", "#1c4a75");
