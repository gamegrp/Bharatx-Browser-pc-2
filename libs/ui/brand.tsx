import logo from "./assets/Floorp_Logo_B_Dark.svg";
import type { BrandProps } from "./types.ts";
const logoUrl = new URL(logo, import.meta.url).href;
export function FloorpBrand({ onDark = false }: BrandProps) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 10,
        color: onDark ? "#fff" : "inherit",
      }}
    >
      <img src={logoUrl} alt="BharatX Browser" width="42" height="42" />
      <strong style={{ fontSize: 18, whiteSpace: "nowrap" }}>
        BharatX Browser
      </strong>
    </span>
  );
}
