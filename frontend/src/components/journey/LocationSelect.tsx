import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import type { Coordinate } from "../../api/types";
import { MELBOURNE_LANDMARKS } from "../../constants/landmarks";
import styles from "./LocationSelect.module.css";

interface LocationSelectProps {
  label: string;
  kind: "origin" | "destination";
  value: Coordinate | null;
  selectedLandmarkId: string | null;
  onSelectLandmark: (landmarkId: string) => void;
  isPicking: boolean;
  onTogglePicking: () => void;
}

interface LocationOption {
  value: string;
  label: string;
  disabled?: boolean;
}

function MapPinIcon() {
  return (
    <svg
      width="25"
      height="25"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
      <circle cx="12" cy="10" r="2.5" />
      <path d="M6 21h12" />
    </svg>
  );
}

export function LocationSelect({
  label,
  kind,
  value,
  selectedLandmarkId,
  onSelectLandmark,
  isPicking,
  onTogglePicking,
}: LocationSelectProps) {
  const selectId = useId();
  const listboxId = `${selectId}-listbox`;
  const labelId = `${selectId}-label`;

  const rootRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const isCustomPoint =
    value !== null && selectedLandmarkId === null;

  const selectedValue = isCustomPoint
    ? "__custom__"
    : selectedLandmarkId ?? "";

  const options: LocationOption[] = [
    {
      value: "",
      label,
    },
    ...(isCustomPoint
      ? [
          {
            value: "__custom__",
            label: "Custom map point",
            disabled: true,
          },
        ]
      : []),
    ...MELBOURNE_LANDMARKS.map((landmark) => ({
      value: landmark.id,
      label: landmark.name,
    })),
  ];

  const selectedOption = options.find(
    (option) => option.value === selectedValue,
  );

  const enabledIndexes = options
    .map((option, index) => (option.disabled ? -1 : index))
    .filter((index) => index !== -1);

  function openMenu() {
    const selectedIndex = options.findIndex(
      (option) =>
        option.value === selectedValue && !option.disabled,
    );

    setActiveIndex(
      selectedIndex >= 0 ? selectedIndex : enabledIndexes[0] ?? 0,
    );

    setIsOpen(true);
  }

  function moveActive(direction: 1 | -1) {
    const currentPosition = enabledIndexes.indexOf(activeIndex);

    let nextPosition: number;

    if (currentPosition === -1) {
      nextPosition = direction === 1 ? 0 : enabledIndexes.length - 1;
    } else {
      nextPosition =
        (currentPosition + direction + enabledIndexes.length) %
        enabledIndexes.length;
    }

    setActiveIndex(enabledIndexes[nextPosition]);
  }

  function selectOption(index: number) {
    const option = options[index];

    if (!option || option.disabled) return;

    onSelectLandmark(option.value);
    setActiveIndex(index);
    setIsOpen(false);
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLButtonElement>,
  ) {
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();

        if (isOpen) {
          moveActive(1);
        } else {
          openMenu();
        }
        break;

      case "ArrowUp":
        event.preventDefault();

        if (isOpen) {
          moveActive(-1);
        } else {
          openMenu();
        }
        break;

      case "Home":
        if (isOpen) {
          event.preventDefault();
          setActiveIndex(enabledIndexes[0]);
        }
        break;

      case "End":
        if (isOpen) {
          event.preventDefault();
          setActiveIndex(
            enabledIndexes[enabledIndexes.length - 1],
          );
        }
        break;

      case "Enter":
      case " ":
        event.preventDefault();

        if (isOpen) {
          selectOption(activeIndex);
        } else {
          openMenu();
        }
        break;

      case "Escape":
        event.preventDefault();
        setIsOpen(false);
        break;
    }
  }

  useEffect(() => {
    function handleOutsideClick(event: PointerEvent) {
      if (
        rootRef.current &&
        !rootRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("pointerdown", handleOutsideClick);

    return () => {
      document.removeEventListener(
        "pointerdown",
        handleOutsideClick,
      );
    };
  }, []);

  useEffect(() => {
    if (!isOpen) return;

    const activeOption =
      listRef.current?.querySelector<HTMLElement>(
        `[data-option-index="${activeIndex}"]`,
      );

    activeOption?.scrollIntoView({
      block: "nearest",
    });
  }, [activeIndex, isOpen]);

  return (
    <div className={styles.fieldRow}>
      <span
        className={
          kind === "origin"
            ? styles.originMarker
            : styles.destinationMarker
        }
        aria-hidden="true"
      />

      <div className={styles.field}>
        <span
          id={labelId}
          className="visually-hidden"
        >
          {label}
        </span>

        <div className={styles.inputShell}>
          <div
            className={styles.selectControl}
            ref={rootRef}
          >
            <button
              id={selectId}
              type="button"
              className={styles.selectButton}
              aria-labelledby={labelId}
              aria-haspopup="listbox"
              aria-expanded={isOpen}
              aria-controls={listboxId}
              aria-activedescendant={
                isOpen
                  ? `${selectId}-option-${activeIndex}`
                  : undefined
              }
              onClick={() => {
                if (isOpen) {
                  setIsOpen(false);
                } else {
                  openMenu();
                }
              }}
              onKeyDown={handleKeyDown}
              onBlur={() => setIsOpen(false)}
            >
              <span className={styles.selectedText}>
                {selectedOption?.label ?? label}
              </span>

              <span
                className={`${styles.chevron} ${
                  isOpen ? styles.chevronOpen : ""
                }`}
                aria-hidden="true"
              >
                ▾
              </span>
            </button>

            {isOpen && (
              <ul
                ref={listRef}
                id={listboxId}
                className={styles.optionList}
                role="listbox"
                aria-labelledby={labelId}
              >
                {options.map((option, index) => {
                  const isSelected =
                    option.value === selectedValue;
                  const isActive = index === activeIndex;

                  return (
                    <li
                      key={`${option.value}-${index}`}
                      id={`${selectId}-option-${index}`}
                      role="option"
                      aria-selected={isSelected}
                      aria-disabled={option.disabled}
                      data-option-index={index}
                      className={[
                        styles.option,
                        isActive ? styles.optionActive : "",
                        isSelected ? styles.optionSelected : "",
                        option.disabled
                          ? styles.optionDisabled
                          : "",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                      onMouseEnter={() => {
                        if (!option.disabled) {
                          setActiveIndex(index);
                        }
                      }}
                      onPointerDown={(event) => {
                        event.preventDefault();
                        selectOption(index);
                      }}
                    >
                      <span>{option.label}</span>

                      {isSelected && (
                        <span
                          className={styles.optionCheck}
                          aria-hidden="true"
                        >
                          ✓
                        </span>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <button
            type="button"
            className={`${styles.pickButton} ${
              isPicking ? styles.pickButtonActive : ""
            }`}
            aria-label={`Pick ${label.toLowerCase()} on map`}
            aria-pressed={isPicking}
            title={
              isPicking
                ? "Cancel map selection"
                : "Pick on map"
            }
            onClick={onTogglePicking}
          >
            <MapPinIcon />
          </button>
        </div>

        {isPicking && (
          <p className={styles.hint} role="status">
            Click anywhere on the map to set the{" "}
            {label.toLowerCase()} location.
          </p>
        )}

        {isCustomPoint && !isPicking && (
          <p className={styles.customPoint}>
            Selected point: {value.lat.toFixed(4)},{" "}
            {value.lng.toFixed(4)}
          </p>
        )}
      </div>
    </div>
  );
}