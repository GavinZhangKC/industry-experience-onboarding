import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

import type {
  RefugeCategory,
} from "../../api/types";

import styles from "./RefugeTypeFilter.module.css";

interface RefugeTypeFilterProps {
  value: RefugeCategory | null;

  onChange: (
    value: RefugeCategory | null,
  ) => void;

  disabled?: boolean;
}

interface FilterOption {
  value: RefugeCategory | null;
  label: string;
}

const OPTIONS: FilterOption[] = [
  {
    value: null,
    label: "All spaces",
  },
  {
    value: "green_space",
    label: "Parks and gardens",
  },
  {
    value: "indoor",
    label: "Indoor spaces",
  },
];

export function RefugeTypeFilter({
  value,
  onChange,
  disabled = false,
}: RefugeTypeFilterProps) {
  const buttonId = useId();
  const listboxId = `${buttonId}-listbox`;
  const labelId = `${buttonId}-label`;

  const rootRef =
    useRef<HTMLDivElement>(null);

  const [isOpen, setIsOpen] =
    useState(false);

  const selectedIndex = Math.max(
    0,
    OPTIONS.findIndex(
      (option) => option.value === value,
    ),
  );

  const [activeIndex, setActiveIndex] =
    useState(selectedIndex);

  const selectedOption =
    OPTIONS[selectedIndex];

  function openMenu() {
    if (disabled) return;

    setActiveIndex(selectedIndex);
    setIsOpen(true);
  }

  function selectOption(index: number) {
    const option = OPTIONS[index];

    if (!option) return;

    onChange(option.value);
    setActiveIndex(index);
    setIsOpen(false);
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLButtonElement>,
  ) {
    if (disabled) return;

    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();

        if (!isOpen) {
          openMenu();
        } else {
          setActiveIndex(
            (activeIndex + 1) %
              OPTIONS.length,
          );
        }
        break;

      case "ArrowUp":
        event.preventDefault();

        if (!isOpen) {
          openMenu();
        } else {
          setActiveIndex(
            (activeIndex -
              1 +
              OPTIONS.length) %
              OPTIONS.length,
          );
        }
        break;

      case "Home":
        if (isOpen) {
          event.preventDefault();
          setActiveIndex(0);
        }
        break;

      case "End":
        if (isOpen) {
          event.preventDefault();
          setActiveIndex(
            OPTIONS.length - 1,
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
    function handleOutsideClick(
      event: PointerEvent,
    ) {
      if (
        rootRef.current &&
        !rootRef.current.contains(
          event.target as Node,
        )
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener(
      "pointerdown",
      handleOutsideClick,
    );

    return () => {
      document.removeEventListener(
        "pointerdown",
        handleOutsideClick,
      );
    };
  }, []);

  return (
    <div className={styles.field}>
      <span
        id={labelId}
        className={styles.label}
      >
        Space type
      </span>

      <div
        ref={rootRef}
        className={styles.selectControl}
      >
        <button
          id={buttonId}
          type="button"
          className={styles.selectButton}
          disabled={disabled}
          aria-labelledby={`${labelId} ${buttonId}`}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          aria-controls={listboxId}
          aria-activedescendant={
            isOpen
              ? `${buttonId}-option-${activeIndex}`
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
        >
          <span>
            {selectedOption.label}
          </span>

          <span
            className={`${styles.chevron} ${
              isOpen
                ? styles.chevronOpen
                : ""
            }`}
            aria-hidden="true"
          >
            ▾
          </span>
        </button>

        {isOpen && (
          <ul
            id={listboxId}
            className={styles.optionList}
            role="listbox"
            aria-labelledby={labelId}
          >
            {OPTIONS.map(
              (option, index) => {
                const isSelected =
                  option.value === value;

                const isActive =
                  index === activeIndex;

                return (
                  <li
                    key={
                      option.value ?? "all"
                    }
                    id={`${buttonId}-option-${index}`}
                    role="option"
                    aria-selected={
                      isSelected
                    }
                    className={[
                      styles.option,
                      isActive
                        ? styles.optionActive
                        : "",
                      isSelected
                        ? styles.optionSelected
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onMouseEnter={() =>
                      setActiveIndex(index)
                    }
                    onPointerDown={(
                      event,
                    ) => {
                      event.preventDefault();
                      selectOption(index);
                    }}
                  >
                    <span>
                      {option.label}
                    </span>

                    {isSelected && (
                      <span
                        className={
                          styles.optionCheck
                        }
                        aria-hidden="true"
                      >
                        ✓
                      </span>
                    )}
                  </li>
                );
              },
            )}
          </ul>
        )}
      </div>
    </div>
  );
}