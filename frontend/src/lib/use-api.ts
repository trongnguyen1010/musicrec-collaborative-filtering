"use client";

import { useEffect, useState } from "react";

type State<T> = { key: string; data?: T; error?: string };

/**
 * Chạy `load` mỗi khi `key` đổi và chỉ giữ câu trả lời của key mới nhất.
 * `loading` được suy ra (key của câu trả lời khác key đang yêu cầu), nên effect
 * không bao giờ đặt state đồng bộ.
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
    // `load` được tạo lại mỗi lần render; `key` đã bao gồm mọi thứ nó phụ thuộc.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  const current = state?.key === key ? state : null;
  return {
    data: current?.data,
    /** Câu trả lời thành công gần nhất (có thể của key cũ); giúp danh sách chuyển động giữa hai lần trả lời. */
    latest: state?.data,
    error: current?.error,
    loading: key !== null && current === null,
  };
}
