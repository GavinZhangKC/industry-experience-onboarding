import styles from "./SensoryPreferences.module.css";
import { type PreferenceState } from "../../constants/preferences";

const OPTIONS: Array<{
  key: keyof PreferenceState;
  label: string;
}> = [
  {
    key: "avoidNoise",
    label: "Avoid noisy areas",
  },
  {
    key: "avoidCrowds",
    label: "Avoid crowded areas",
  },
  {
    key: "avoidConstruction",
    label: "Avoid construction zones",
  },
  {
    key: "avoidMajorEvents",
    label: "Avoid major events",
  },
];

interface SensoryPreferencesProps {
  preferences: PreferenceState;
  onChange: (preferences: PreferenceState) => void;
}

// US 1.3: avoidCrowds is the one preference with a real backend behind it —
// it maps to sensitivity_threshold on the routes request (see App.tsx). The
// other three toggles are honestly still decorative: there's no
// disruption/event/noise data feeding the scorer yet. Left visible rather
// than removed, since hiding them would be a bigger UX change than this fix
// warrants — but worth being upfront about which one actually does
// something, if asked.
export function SensoryPreferences({ preferences, onChange }: SensoryPreferencesProps) {
  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.legend}>
        Sensory preferences:
      </legend>

      <div className={styles.options}>
        {OPTIONS.map((option) => (
          <label className={styles.option} key={option.key}>
            <input
              className={styles.input}
              type="checkbox"
              role="switch"
              checked={preferences[option.key]}
              onChange={(event) =>
                onChange({
                  ...preferences,
                  [option.key]: event.target.checked,
                })
              }
            />

            <span className={styles.track} aria-hidden="true">
              <span className={styles.thumb} />
            </span>

            <span className={styles.label}>
              {option.label}
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
