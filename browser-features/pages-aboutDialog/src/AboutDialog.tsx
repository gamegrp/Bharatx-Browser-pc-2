import { BHARATX } from "../../../libs/shared/bharatx-brand.ts";
interface BrowserWindow {
  openTrustedLinkIn: (url: string, where: string) => void;
  focus: () => void;
}
declare const Services: {
  wm: { getMostRecentWindow: (type: string) => BrowserWindow | null };
};
function openPage(url: string): void {
  const win = Services.wm.getMostRecentWindow("navigator:browser");
  if (win) {
    win.openTrustedLinkIn(url, "tab");
    win.focus();
  }
}
export function AboutDialog() {
  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        padding: "28px 34px",
        minWidth: 460,
        maxWidth: 680,
        lineHeight: 1.65,
      }}
    >
      <img
        src="chrome://branding/content/about-logo@2x.png"
        alt={BHARATX.name}
        width="100"
        height="100"
      />
      <h1 style={{ fontSize: 30, marginBottom: 0 }}>{BHARATX.name}</h1>
      <p>Version {BHARATX.version}</p>
      <p>
        <strong>Developed by {BHARATX.developer}</strong>
        <br />
        {BHARATX.origin}
      </p>
      <p>Get updates from Microsoft Store → Library.</p>
      <p>
        <a
          href={`mailto:${BHARATX.email}`}
          onClick={(event) => {
            event.preventDefault();
            openPage(`mailto:${BHARATX.email}`);
          }}
        >
          {BHARATX.email}
        </a>
      </p>
      <nav
        aria-label="Information"
        style={{ display: "flex", flexWrap: "wrap", gap: 18 }}
      >
        {[["Website", BHARATX.website], ["Privacy Policy", BHARATX.privacy], [
          "Disclaimer",
          BHARATX.disclaimer,
        ], ["Open-source licenses", "about:license"]].map(([label, url]) => (
          <a
            href={url}
            key={label}
            onClick={(event) => {
              event.preventDefault();
              openPage(url);
            }}
          >
            {label}
          </a>
        ))}
      </nav>
      <p style={{ fontSize: 12 }}>
        © 2026 Nitai Studio. Third-party components retain their respective
        licenses and copyright notices.
      </p>
      <button type="button" onClick={() => globalThis.close()}>Close</button>
    </main>
  );
}
