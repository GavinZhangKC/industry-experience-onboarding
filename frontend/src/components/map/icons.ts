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

export const originIcon = L.divIcon({
  className: "",
  html: `<div style="
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #174f9e;
      border: 4px solid #ffffff;
      box-shadow:
        0 0 0 3px #dbe9ff,
        0 2px 5px rgba(0,0,0,0.28);
    "></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

export const destinationIcon = L.divIcon({
  className: "",
  html: `<div style="
      position: relative;
      width: 28px;
      height: 28px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      background: #174f9e;
      border: 3px solid #ffffff;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    ">
      <span style="
        position: absolute;
        width: 7px;
        height: 7px;
        top: 7px;
        left: 7px;
        border-radius: 50%;
        background: #ffffff;
      "></span>
    </div>`,
  iconSize: [28, 34],
  iconAnchor: [14, 30],
});
export const quietSpaceIcon = pinIcon("Q", "#3e6b9b");
export const quietSpaceSelectedIcon = pinIcon("Q", "#1c4a75");
