import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { BHARATX } from "../../../../libs/shared/bharatx-brand.ts";
import { type ReleaseNotesMode } from "../../../modules/common/release-notes.ts";

// Preserve the setup API while removing upstream advertising exceptions.
export function useReleaseNotesChoice(_allowNewDefault = false) {
  const [ready, setReady] = useState(false);
  const saving = false;
  const error = false;
  const mode: ReleaseNotesMode = "disabled";
  const setMode = useCallback((_value: ReleaseNotesMode) => {}, []);
  useEffect(() => {
    setReady(true);
  }, []);
  function confirm(): Promise<boolean> {
    return Promise.resolve(ready);
  }

  return { mode, setMode, currentMode: mode, ready, saving, error, confirm };
}
const SetupReleaseNotesContext = createContext<
  {
    choice: ReturnType<typeof useReleaseNotesChoice>;
    reviewed: boolean;
    setReviewed: (value: boolean) => void;
  } | null
>(null);
export function SetupReleaseNotesProvider(
  { children }: { children: ReactNode },
) {
  const choice = useReleaseNotesChoice(true);
  const [reviewed, setReviewed] = useState(false);
  return (
    <SetupReleaseNotesContext.Provider
      value={{ choice, reviewed, setReviewed }}
    >
      {children}
    </SetupReleaseNotesContext.Provider>
  );
}
export function useSetupReleaseNotesChoice() {
  const value = useContext(SetupReleaseNotesContext);
  if (!value) throw new Error("Missing setup context");
  return value;
}
export function ReleaseNotesPrompt() {
  return (
    <main style={{ padding: 32, fontFamily: "system-ui", lineHeight: 1.8 }}>
      <h1>BharatX Browser</h1>
      <p>Developed by {BHARATX.developer}. {BHARATX.origin}.</p>
      <p>Use Microsoft Store to get browser updates.</p>
      <p>
        <a href={BHARATX.privacy}>Privacy Policy</a> ·{" "}
        <a href={BHARATX.disclaimer}>Disclaimer</a>
      </p>
      <p>
        <a href={`mailto:${BHARATX.email}`}>Contact support</a>
      </p>
      <button
        type="button"
        onClick={() =>
          globalThis.location.replace("about:newtab")}
      >
        Continue browsing
      </button>
    </main>
  );
}
