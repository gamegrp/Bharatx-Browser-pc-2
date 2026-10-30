export default function WhatsNewPage() {
  return (
    <main style={{ padding: 32, fontFamily: "system-ui", lineHeight: 1.8 }}>
      <h1>BharatX Browser 1.36.0</h1>
      <p>Developed by Nitaistudio. Made in India.</p>
      <p>
        Updated browser branding, local policy pages and Microsoft Store
        packaging.
      </p>
      <p>
        <a href="chrome://noraneko-pages-aboutdialog/content/bharatx-about.html">
          About and support
        </a>
      </p>
      <button
        type="button"
        onClick={() =>
          globalThis.location.replace("about:newtab")}
      >
        Start browsing
      </button>
    </main>
  );
}
