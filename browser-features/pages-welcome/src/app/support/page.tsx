import { useEffect } from "react";
import Navigation from "../../components/Navigation.tsx";
import { useSetupReleaseNotesChoice } from "../../components/ReleaseNotesChoice.tsx";
import { BHARATX } from "../../../../../libs/shared/bharatx-brand.ts";
export default function SupportPage() {
  const { choice, setReviewed } = useSetupReleaseNotesChoice();
  useEffect(() => {
    if (choice.ready) {
      choice.setMode("disabled");
      setReviewed(true);
    }
  }, [choice.ready, setReviewed]);
  return (
    <div>
      <h2>Privacy and support</h2>
      <p>Developed by {BHARATX.developer}. {BHARATX.origin}.</p>
      <p>
        Browsing history, cookies and bookmarks are stored in your browser
        profile. Websites and optional services process data under their own
        policies.
      </p>
      <p>
        <a href={BHARATX.privacy} target="_blank" rel="noopener noreferrer">
          Read Privacy Policy
        </a>
      </p>
      <p>
        <a href={BHARATX.disclaimer} target="_blank" rel="noopener noreferrer">
          Read Disclaimer
        </a>
      </p>
      <p>
        <a href={`mailto:${BHARATX.email}`}>{BHARATX.email}</a>
      </p>
      <p>
        <a href={BHARATX.website} target="_blank" rel="noopener noreferrer">
          Developer website
        </a>
      </p>
      {choice.error && (
        <p role="alert">Unable to save setup. Please try again.</p>
      )}
      <Navigation />
    </div>
  );
}
