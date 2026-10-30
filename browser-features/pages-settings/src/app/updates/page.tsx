import { BHARATX } from "../../../../../libs/shared/bharatx-brand.ts";
export default function Page() {
  return (
    <div className="floorp-settings-page">
      <h1 className="floorp-page-heading">BharatX Browser updates</h1>
      <p>Version {BHARATX.version}</p>
      <p>
        For the Microsoft Store edition, open Microsoft Store, select Library,
        and check for updates.
      </p>
      <p>
        Updates for this edition are distributed by Nitai Studio through
        Microsoft Store.
      </p>
      <p>
        <a href={`mailto:${BHARATX.email}`}>Contact support</a>
      </p>
    </div>
  );
}
