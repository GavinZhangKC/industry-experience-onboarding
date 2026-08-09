import { useState } from "react";
import styles from "./SensoryPreferences.module.css";

interface PreferenceState {
  avoidNoise: boolean;
  avoidCrowds: boolean;
  avoidConstruction: boolean;
  avoidMajorEvents: boolean;
}

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

export function SensoryPreferences() {
  const [preferences, setPreferences] =
    useState<PreferenceState>({
      avoidNoise: true,
      avoidCrowds: true,
      avoidConstruction: true,
      avoidMajorEvents: true,
    });

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
                setPreferences({
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