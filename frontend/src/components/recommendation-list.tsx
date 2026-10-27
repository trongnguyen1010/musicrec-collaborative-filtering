"use client";

import { AnimatePresence, motion } from "motion/react";
import type { Recommendation } from "@/lib/api";
import { explainReason, int } from "@/lib/format";
import { ArtistAvatar, Badge } from "./ui";

/** Width of a listener bar on a log scale shared by every list on screen. */
export function listenerShare(listeners: number, maxListeners: number): number {
  return Math.log1p(listeners) / Math.log1p(Math.max(maxListeners, 1));
}

/** Listener bar: longer means more listeners on train (more popular). */
export function ListenerBar({ share }: { share: number }) {
  return (
    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
      <div
        className="h-full rounded-full bg-ice transition-[width] duration-700 ease-out"
        style={{ width: `${Math.max(share * 100, 2)}%` }}
      />
    </div>
  );
}

/** One ranked list with staggered, re-orderable rows. */
export function RecommendationList({
  items,
  maxListeners,
  highlight,
}: {
  items: Recommendation[];
  maxListeners: number;
  highlight?: (item: Recommendation) => string | null;
}) {
  return (
    <ol className="space-y-1.5">
      <AnimatePresence initial={false}>
        {items.map((item, index) => {
          const note = highlight?.(item);
          return (
            <motion.li
              layout
              key={item.item_id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0, transition: { delay: index * 0.025 } }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ type: "spring", stiffness: 420, damping: 34 }}
              className="flex items-center gap-3 rounded-xl px-2 py-1.5 hover:bg-white/5"
            >
              <span className="w-5 text-right font-mono text-sm tabular-nums text-muted">
                {item.rank}
              </span>
              <ArtistAvatar name={item.name} src={item.picture_url} size={36} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <a
                    href={item.url || undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="truncate font-medium hover:underline"
                  >
                    {item.name}
                  </a>
                  {note && <Badge tone="mint">{note}</Badge>}
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <ListenerBar share={listenerShare(item.listeners, maxListeners)} />
                  <span className="shrink-0 whitespace-nowrap text-right font-mono text-sm tabular-nums text-muted">
                    {int(item.listeners)} người nghe
                  </span>
                </div>
                <p className="mt-1 truncate text-sm text-muted">{explainReason(item.reason)}</p>
              </div>
            </motion.li>
          );
        })}
      </AnimatePresence>
    </ol>
  );
}
