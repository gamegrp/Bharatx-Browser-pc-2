import { BHARATX } from "../../../../../libs/shared/bharatx-brand.ts";
export default function Page() {
  return (
    <div className="floorp-settings-page">
      <header className="floorp-page-header">
        <img
          src="chrome://branding/content/about-logo@2x.png"
          alt={BHARATX.name}
          width="96"
          height="96"
        />
        <h1 className="floorp-page-heading">{BHARATX.name}</h1>
        <p className="floorp-page-description">Version {BHARATX.version}</p>
      </header>
      <section className="floorp-settings-sections" style={{ lineHeight: 1.8 }}>
        <div>
          <h2>About</h2>
          <p>Developed by {BHARATX.developer}</p>
          <p>{BHARATX.origin}</p>
          <p>
            A desktop browser with tabs, workspaces, extensions, bookmarks and
            privacy controls.
          </p>
        </div>
        <div>
          <h2>Support</h2>
          <p>
            <a href={`mailto:${BHARATX.email}`}>{BHARATX.email}</a>
          </p>
          <p>
            <a href={BHARATX.website} target="_blank" rel="noopener noreferrer">
              Developer website
            </a>
          </p>
        </div>
        <nav
          aria-label="Policies"
          style={{ display: "flex", flexWrap: "wrap", gap: 24 }}
        >
          <a href={BHARATX.privacy} target="_blank" rel="noopener noreferrer">
            Privacy Policy
          </a>
          <a
            href={BHARATX.disclaimer}
            target="_blank"
            rel="noopener noreferrer"
          >
            Disclaimer
          </a>
          <a href="about:license" target="_blank" rel="noopener noreferrer">
            Open-source licenses
          </a>
        </nav>
        <p>
          © 2026 Nitai Studio. Third-party components retain their own licenses
          and copyright notices.
        </p>
        <p>
          Source for covered components and our modifications is available
          without charge. Request version {BHARATX.version} from{" "}
          {BHARATX.email}.
        </p>
      </section>
    </div>
  );
}
