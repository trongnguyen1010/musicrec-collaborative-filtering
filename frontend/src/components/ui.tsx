"use client";

import { AnimatePresence, animate, motion, useInView, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState, type ReactNode } from "react";

type Glow = "none" | "ice" | "mint" | "blush";

export function Card({
  children,
  className = "",
  glow = "none",
}: {
  children: ReactNode;
  className?: string;
  glow?: Glow;
}) {
  const halo = glow === "none" ? "" : `glow-${glow}`;
  return <section className={`glass rounded-2xl p-5 ${halo} ${className}`}>{children}</section>;
}

type Tone = "neutral" | "danger" | "mint" | "blush" | "lilac";
const TONES: Record<Tone, string> = {
  neutral: "bg-surface-2 text-muted",
  danger: "bg-danger-soft text-danger",
  mint: "bg-mint-soft text-mint",
  blush: "bg-blush-soft text-blush",
  lilac: "bg-lilac-soft text-ice",
};

/** Animated number that counts from its previous value; `format` renders each frame. */
export function Counter({ value, format }: { value: number; format: (v: number) => string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const previous = useRef(0);
  const inView = useInView(ref, { once: true });
  const reduce = useReducedMotion();
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (reduce || !inView) {
      node.textContent = format(value);
      return;
    }
    const controls = animate(previous.current, value, {
      duration: 0.8,
      ease: "easeOut",
      onUpdate: (v) => {
        node.textContent = format(v);
      },
    });
    previous.current = value;
    // Guarantee the exact final value even if animation frames are throttled.
    const settle = setTimeout(() => {
      controls.stop();
      node.textContent = format(value);
    }, 1000);
    return () => {
      controls.stop();
      clearTimeout(settle);
    };
  }, [value, format, inView, reduce]);
  return (
    <span ref={ref} className="font-mono tabular-nums">
      {format(value)}
    </span>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: Tone }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${TONES[tone]}`}>
      {children}
    </span>
  );
}

export function Notice({ children, tone = "blush" }: { children: ReactNode; tone?: Tone }) {
  return (
    <div role="status" className={`rounded-xl px-4 py-3 text-sm ${TONES[tone]}`}>
      {children}
    </div>
  );
}

export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
  label: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-full bg-surface-2 p-1">
      {options.map((option) => (
        <button
          key={option.value}
          role="radio"
          aria-checked={value === option.value}
          onClick={() => onChange(option.value)}
          className={`rounded-full px-3 py-1 text-sm transition-colors ${
            value === option.value
              ? "bg-lilac/25 text-text shadow-[inset_0_0_0_1px_rgba(140,200,255,0.5)]"
              : "text-muted hover:text-text"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

const PALETTE = ["#4f7dd9", "#6c63c9", "#2f8f86", "#3e86b0", "#7a6fd0", "#4a90c2"];

/** Last.fm 2011 picture links are mostly dead; fall back to coloured initials. */
export function ArtistAvatar({ name, src, size = 40 }: { name: string; src: string; size?: number }) {
  const [failed, setFailed] = useState(!src);
  const color = PALETTE[[...name].reduce((sum, ch) => sum + ch.charCodeAt(0), 0) % PALETTE.length];
  const style = { width: size, height: size };
  if (!failed) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt=""
        style={style}
        className="shrink-0 rounded-full object-cover"
        onError={() => setFailed(true)}
        loading="lazy"
      />
    );
  }
  return (
    <span
      aria-hidden
      style={{ ...style, background: color }}
      className="grid shrink-0 place-items-center rounded-full text-sm font-semibold text-white"
    >
      {name.trim().charAt(0).toUpperCase() || "?"}
    </span>
  );
}

export function Spinner({ label = "Đang tải" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted" role="status">
      <span className="size-4 animate-spin rounded-full border-2 border-border border-t-danger" />
      {label}
    </div>
  );
}

/** Show `pageSize` items at a time with numbered page buttons. */
export function usePaged<T>(items: T[], pageSize: number, resetKey: string) {
  const [state, setState] = useState({ key: resetKey, page: 0 });
  const page = state.key === resetKey ? state.page : 0;
  const pages = Math.max(1, Math.ceil(items.length / pageSize));
  return {
    visible: items.slice(page * pageSize, page * pageSize + pageSize),
    page,
    pages,
    setPage: (p: number) => setState({ key: resetKey, page: Math.min(Math.max(p, 0), pages - 1) }),
  };
}

export function Pager({
  page,
  pages,
  setPage,
  label,
}: {
  page: number;
  pages: number;
  setPage: (p: number) => void;
  label: string;
}) {
  if (pages <= 1) return null;
  const button = "grid h-9 min-w-9 place-items-center rounded-lg px-2 text-sm transition-colors";
  return (
    <nav aria-label={label} className="flex items-center justify-center gap-1.5 pt-3">
      <button
        onClick={() => setPage(page - 1)}
        disabled={page === 0}
        className={`${button} text-muted hover:bg-white/5 hover:text-text disabled:opacity-30`}
      >
        Trước
      </button>
      {Array.from({ length: pages }, (_, i) => (
        <button
          key={i}
          onClick={() => setPage(i)}
          aria-current={i === page ? "page" : undefined}
          className={`${button} font-mono ${
            i === page ? "bg-ice-soft text-ice" : "text-muted hover:bg-white/5 hover:text-text"
          }`}
        >
          {i + 1}
        </button>
      ))}
      <button
        onClick={() => setPage(page + 1)}
        disabled={page === pages - 1}
        className={`${button} text-muted hover:bg-white/5 hover:text-text disabled:opacity-30`}
      >
        Sau
      </button>
    </nav>
  );
}

/** A light band sweeping across its (relative, overflow-hidden) parent whenever `trigger` changes. */
export function Sweep({ trigger }: { trigger: string }) {
  return (
    <AnimatePresence>
      <motion.span
        key={trigger}
        aria-hidden
        className="pointer-events-none absolute inset-y-0 -left-1/3 z-10 w-1/3 bg-gradient-to-r from-transparent via-ice/20 to-transparent"
        initial={{ x: "0%" }}
        animate={{ x: "450%" }}
        transition={{ duration: 0.9, ease: "easeInOut" }}
      />
    </AnimatePresence>
  );
}
