"use client";

import { AnimatePresence, motion } from "motion/react";
import { useDeferredValue, useState } from "react";
import { RecommendationList } from "@/components/recommendation-list";
import {
  ArtistAvatar,
  Card,
  Notice,
  Pager,
  Segmented,
  Spinner,
  Sweep,
  usePaged,
} from "@/components/ui";
import { api, type Artist, type RecommendResponse } from "@/lib/api";
import { int, num } from "@/lib/format";
import { m2Row } from "@/lib/results";
import { useApi } from "@/lib/use-api";

const MAX_ARTISTS = 5;
const K_OPTIONS = ["5", "10", "20"] as const;
const FALLBACK_TEXT: Record<string, string> = {
  empty_profile: "Chưa chọn nghệ sĩ nào: hệ thống dùng Popularity (nghệ sĩ phổ biến nhất).",
  no_profile_artist_in_m2_catalog:
    "Không nghệ sĩ nào bạn chọn nằm trong danh mục M2, nên M2 chỉ còn thành phần phổ biến.",
};

export function NewUser() {
  const [query, setQuery] = useState("");
  const deferred = useDeferredValue(query.trim());
  const [chosen, setChosen] = useState<Artist[]>([]);
  const [k, setK] = useState<(typeof K_OPTIONS)[number]>("10");
  const search = useApi(`artists:${deferred}`, () => api.artists(deferred, 18));
  const ids = chosen.map((a) => a.item_id);
  const result = useApi(`new:${ids.join(",")}:${k}`, () =>
    api.recommend({ history: ids.map((item_id) => ({ item_id })), k: Number(k) }),
  );
  const full = chosen.length >= MAX_ARTISTS;
  const n3 = { m2: m2Row(3, "m2"), popularity: m2Row(3, "popularity") };

  function toggle(artist: Artist) {
    setChosen((current) =>
      current.some((a) => a.item_id === artist.item_id)
        ? current.filter((a) => a.item_id !== artist.item_id)
        : current.length < MAX_ARTISTS
          ? [...current, artist]
          : current,
    );
  }

  const data = result.latest;
  const hybrid = data?.model === "m2" && !data.fallback_used;
  return (
    <div className="space-y-6">
      <header className="rise space-y-2">
        <p className="font-mono text-xs tracking-widest text-mint">COLD START · M2 HYBRID</p>
        <h1 className="text-3xl font-bold tracking-tight">Người dùng mới</h1>
        <p className="max-w-3xl text-muted">
          Chọn từ 1 đến {MAX_ARTISTS} nghệ sĩ bạn thích. M2 trộn người nghe tương tự (ItemCF), thẻ
          nội dung và độ phổ biến, không cần học lại mô hình.
        </p>
      </header>

      <Slots chosen={chosen} onRemove={toggle} onClear={() => setChosen([])} />

      <div className="grid gap-6 lg:grid-cols-[24rem_1fr]">
        <Card className="h-fit space-y-4">
          <div>
            <label htmlFor="artist-search" className="text-sm font-medium">
              Tìm nghệ sĩ
            </label>
            <input
              id="artist-search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ví dụ: Coldplay, Lady Gaga, Muse"
              className="mt-1 w-full rounded-xl border border-border bg-bg/60 px-3 py-2"
              autoComplete="off"
            />
          </div>
          <p className="text-sm text-muted">
            {deferred ? "Kết quả tìm kiếm" : "Nghe nhiều nhất trong danh mục"}
          </p>
          {search.loading && !search.latest && <Spinner />}
          {search.error && <Notice tone="danger">{search.error}</Notice>}
          {search.data?.length === 0 && <p className="text-sm text-muted">Không tìm thấy.</p>}
          <motion.div layout className="flex flex-wrap gap-2">
            <AnimatePresence initial={false} mode="popLayout">
              {(search.data ?? search.latest ?? []).map((artist) => {
                const selected = ids.includes(artist.item_id);
                return (
                  <motion.button
                    layout
                    key={artist.item_id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.92 }}
                    transition={{ type: "spring", stiffness: 500, damping: 26 }}
                    onClick={() => toggle(artist)}
                    disabled={!selected && full}
                    aria-pressed={selected}
                    className={`flex items-center gap-1.5 rounded-full border py-1 pl-1 pr-3 text-sm disabled:opacity-35 ${
                      selected
                        ? "border-mint bg-mint-soft text-text shadow-[0_0_16px_rgba(74,222,128,0.35)]"
                        : "border-border bg-white/5 hover:border-lilac"
                    }`}
                  >
                    <ArtistAvatar name={artist.name} src={artist.picture_url} size={24} />
                    <span className="max-w-40 truncate">{artist.name}</span>
                    <span className="font-mono text-[13px] text-muted">{int(artist.listeners)}</span>
                  </motion.button>
                );
              })}
            </AnimatePresence>
          </motion.div>
        </Card>

        <div className="min-w-0 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <RegimeBanner hybrid={hybrid} count={chosen.length} ready={!!data} />
            <Segmented
              label="Số gợi ý K"
              value={k}
              onChange={setK}
              options={K_OPTIONS.map((value) => ({ value, label: `K = ${value}` }))}
            />
          </div>
          {data?.fallback_used && data.fallback_reason && (
            <Notice>{FALLBACK_TEXT[data.fallback_reason] ?? data.fallback_reason}</Notice>
          )}
          {result.error && <Notice tone="danger">{result.error}</Notice>}
          {!data && result.loading && <Spinner label="Đang gợi ý" />}
          {data && <Results data={data} sweepKey={ids.join(",")} hybrid={hybrid} />}
          <details className="glass rounded-2xl px-5 py-4 text-sm text-muted">
            <summary className="cursor-pointer font-medium text-text">M2 làm tốt đến đâu trên test?</summary>
            <p className="mt-3">
              Với {n3.m2.users} người dùng để dành và hồ sơ 3 nghệ sĩ, NDCG@10 của M2 là{" "}
              <span className="font-mono text-text">{num(n3.m2.ndcg, 4)}</span>, của Popularity là{" "}
              <span className="font-mono text-text">{num(n3.popularity.ndcg, 4)}</span>; khác biệt không
              có ý nghĩa thống kê. M2 đa dạng hơn: ILD{" "}
              <span className="font-mono text-text">{num(n3.m2.ild, 3)}</span> so với{" "}
              <span className="font-mono text-text">{num(n3.popularity.ild, 3)}</span>.
            </p>
            <p className="mt-2">
              Demo không hỏi số lượt nghe, nên mỗi nghệ sĩ bạn chọn được gán mức nghe trung bình.
            </p>
          </details>
        </div>
      </div>
    </div>
  );
}

function Slots({
  chosen,
  onRemove,
  onClear,
}: {
  chosen: Artist[];
  onRemove: (a: Artist) => void;
  onClear: () => void;
}) {
  return (
    <Card className="flex flex-wrap items-center gap-6">
      <div className="flex flex-wrap gap-4">
        {Array.from({ length: MAX_ARTISTS }, (_, i) => {
          const artist = chosen[i];
          return (
            <div key={i} className="flex w-20 flex-col items-center gap-2">
              <div
                className={`grid size-14 place-items-center rounded-full border-2 ${
                  artist
                    ? "border-mint shadow-[0_0_20px_rgba(74,222,128,0.45)]"
                    : "border-dashed border-white/15"
                }`}
              >
                <AnimatePresence mode="popLayout">
                  {artist && (
                    <motion.button
                      key={artist.item_id}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      transition={{ type: "spring", stiffness: 520, damping: 22 }}
                      onClick={() => onRemove(artist)}
                      aria-label={`Bỏ ${artist.name}`}
                      title="Bấm để bỏ"
                    >
                      <ArtistAvatar name={artist.name} src={artist.picture_url} size={48} />
                    </motion.button>
                  )}
                </AnimatePresence>
              </div>
              <span
                className={`w-full truncate text-center text-sm ${artist ? "text-text" : "text-muted"}`}
                title={artist?.name}
              >
                {artist ? artist.name : " "}
              </span>
            </div>
          );
        })}
      </div>
      <div className="ml-auto flex items-center gap-4">
        <p className="font-mono text-lg">
          {chosen.length}/{MAX_ARTISTS}
        </p>
        {chosen.length > 0 && (
          <button onClick={onClear} className="rounded-lg px-3 py-1.5 text-sm text-ice hover:bg-ice-soft">
            Bỏ chọn hết
          </button>
        )}
      </div>
    </Card>
  );
}

function Results({
  data,
  sweepKey,
  hybrid,
}: {
  data: RecommendResponse;
  sweepKey: string;
  hybrid: boolean;
}) {
  const paged = usePaged(data.recommendations, 5, `${sweepKey}:${data.recommendations.length}`);
  return (
    <Card glow={hybrid ? "mint" : "ice"} className="relative overflow-hidden">
      <Sweep trigger={sweepKey} />
      <RecommendationList
        items={paged.visible}
        maxListeners={Math.max(...data.recommendations.map((r) => r.listeners))}
      />
      <Pager label="Trang gợi ý" {...paged} />
    </Card>
  );
}

function RegimeBanner({ hybrid, count, ready }: { hybrid: boolean; count: number; ready: boolean }) {
  return (
    <motion.div
      layout
      className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${
        hybrid
          ? "bg-gradient-to-r from-lilac/30 to-mint/30 text-text shadow-[0_0_24px_rgba(140,200,255,0.35)]"
          : "bg-blush-soft text-blush"
      }`}
    >
      <span className={`size-2 rounded-full ${hybrid ? "animate-pulse bg-mint" : "bg-blush"}`} />
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={String(hybrid)}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
        >
          {!ready
            ? "Đang chờ API"
            : hybrid
              ? `M2 Hybrid · ${count} nghệ sĩ`
              : "Popularity · dự phòng"}
        </motion.span>
      </AnimatePresence>
    </motion.div>
  );
}
