import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { findQuietSpaces } from "../api/quietSpaces";

import {
  ApiError,
  type Coordinate,
  type QuietSpaceResponse,
  type RefugeCategory,
} from "../api/types";

export const RADIUS_STEPS_M = [
  500,
  1000,
  2000,
] as const;

interface QuietSpacesState {
  data: QuietSpaceResponse | null;
  loading: boolean;
  error: ApiError | null;
  center: Coordinate | null;
}

export function useQuietSpaces() {
  const [state, setState] =
    useState<QuietSpacesState>({
      data: null,
      loading: false,
      error: null,
      center: null,
    });

  const [category, setCategoryState] =
    useState<RefugeCategory | null>(null);

  const activeRequest =
    useRef<AbortController | null>(null);

  const search = useCallback(
    async (
      center: Coordinate,
      radiusM: number = RADIUS_STEPS_M[0],
      selectedCategory:
        | RefugeCategory
        | null = category,
    ) => {
      activeRequest.current?.abort();

      const controller = new AbortController();
      activeRequest.current = controller;

      setState((previous) => ({
        ...previous,
        loading: true,
        error: null,
        center,
      }));

      try {
        const data = await findQuietSpaces(
          center.lat,
          center.lng,
          radiusM,
          5,
          selectedCategory ?? undefined,
          controller.signal,
        );

        if (
          activeRequest.current !== controller
        ) {
          return;
        }

        setState({
          data,
          loading: false,
          error: null,
          center,
        });
      } catch (error) {
        if (
          controller.signal.aborted ||
          activeRequest.current !== controller
        ) {
          return;
        }

        const apiError =
          error instanceof ApiError
            ? error
            : new ApiError({
                code: "internal_error",
                message:
                  "Something went wrong on our side.",
                request_id: null,
              });

        setState({
          data: null,
          loading: false,
          error: apiError,
          center,
        });
      } finally {
        if (
          activeRequest.current === controller
        ) {
          activeRequest.current = null;
        }
      }
    },
    [category],
  );

  const changeCategory = useCallback(
    (
      nextCategory:
        | RefugeCategory
        | null,
    ) => {
      setCategoryState(nextCategory);

      if (state.center) {
        search(
          state.center,
          RADIUS_STEPS_M[0],
          nextCategory,
        );
      }
    },
    [state.center, search],
  );

  const expandRadius = useCallback(() => {
    if (!state.center || !state.data) {
      return;
    }

    const currentIndex =
      RADIUS_STEPS_M.indexOf(
        state.data.radius_m as
          (typeof RADIUS_STEPS_M)[number],
      );

    const nextRadius =
      RADIUS_STEPS_M[currentIndex + 1];

    if (nextRadius === undefined) {
      return;
    }

    search(
      state.center,
      nextRadius,
      category,
    );
  }, [
    state.center,
    state.data,
    category,
    search,
  ]);

  const canExpand =
    state.data !== null &&
    RADIUS_STEPS_M.indexOf(
      state.data.radius_m as
        (typeof RADIUS_STEPS_M)[number],
    ) <
      RADIUS_STEPS_M.length - 1;

  const reset = useCallback(() => {
    activeRequest.current?.abort();
    activeRequest.current = null;

    setCategoryState(null);

    setState({
      data: null,
      loading: false,
      error: null,
      center: null,
    });
  }, []);

  useEffect(() => {
    return () => {
      activeRequest.current?.abort();
    };
  }, []);

  return {
    ...state,
    category,
    search,
    changeCategory,
    expandRadius,
    canExpand,
    reset,
  };
}