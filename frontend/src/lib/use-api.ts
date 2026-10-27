"use client";

import { useEffect, useState } from "react";

type State<T> = { key: string; data?: T; error?: string };

/**
 * Run `load` whenever `key` changes and keep only the answer for the latest key.
 * `loading` is derived (answer key differs from the requested key), so the effect
 * never sets state synchronously.
 */
export function useApi<T>(requested: string | null | false, load: () => Promise<T>) {
  const key = requested || null;
  const [state, setState] = useState<State<T> | null>(null);
  useEffect(() => {
    if (key === null) return;
    let live = true;
    load().then(
      (data) => live && setState({ key, data }),
      (error: unknown) =>
        live && setState({ key, error: error instanceof Error ? error.message : String(error) }),
    );
    return () => {
      live = false;
    };
    // `load` is recreated each render; `key` captures everything it depends on.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  const current = state?.key === key ? state : null;
  return {
    data: current?.data,
    /** Last successful answer, possibly for an older key; lets lists animate between answers. */
    latest: state?.data,
    error: current?.error,
    loading: key !== null && current === null,
  };
}
