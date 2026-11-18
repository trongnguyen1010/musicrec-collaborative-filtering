"use client";

import { motion } from "motion/react";
import { useState } from "react";
import { Card } from "@/components/ui";
import { MODEL_NAMES, num, pct } from "@/lib/format";
import { results, type WarmRow } from "@/lib/results";

type Metric = "ndcg" | "precision" | "recall" | "catalog_coverage" | "arp" | "novelty" | "ild";
const COLUMNS: { key: Metric; label: string; format: (v: number) => string; lower?: boolean }[] = [
  { key: "ndcg", label: "NDCG@10", format: (v) => num(v, 4) },
  { key: "precision", label: "Precision", format: (v) => num(v, 4) },
  { key: "recall", label: "Recall", format: (v) => num(v, 4) },
  { key: "catalog_coverage", label: "Coverage", format: (v) => pct(v, 2) },
  { key: "arp", label: "ARP", format: (v) => num(v, 1), lower: true },
  { key: "novelty", label: "Novelty", format: (v) => num(v, 2) },
  { key: "ild", label: "ILD", format: (v) => num(v, 3) },
];
const RADAR: { key: Metric; label: string; lower?: boolean }[] = [
  { key: "ndcg", label: "NDCG" },
  { key: "catalog_coverage", label: "Coverage" },
  { key: "novelty", label: "Novelty" },
  { key: "ild", label: "ILD" },
  { key: "arp", label: "ARP thấp", lower: true },
];
// Hex values (not CSS variables) so SVG presentation attributes render everywhere.
const COLORS: Record<string, string> = {
  pure_svd: "#4da3ff",
  m1: "#4ade80",
  implicit_als: "#8cc8ff",
  popularity: "#f472b6",
};
const MUTED = "#a8b6d4";

const rows = results.warm_test_k10;
// Hand-placed label offsets so neighbouring points (PureSVD/M1, UserCF/ItemCF) stay readable.
const LABELS: Record<string, { dx: number; dy: number; anchor: "start" | "end" }> = {
  pure_svd: { dx: 10, dy: 14, anchor: "start" },
  m1: { dx: -10, dy: -8, anchor: "end" },
  implicit_als: { dx: -10, dy: -8, anchor: "end" },
  popularity: { dx: -10, dy: -8, anchor: "end" },
  svd: { dx: 0, dy: 18, anchor: "end" },
  user_cf: { dx: 10, dy: -8, anchor: "start" },
  item_cf: { dx: 10, dy: 12, anchor: "start" },
  random: { dx: 10, dy: -6, anchor: "start" },
};

/** Models no other model beats on both axes (higher NDCG and lower ARP). */
function paretoFront(data: WarmRow[]): Set<string> {
  return new Set(
    data
      .filter(
        (a) =>
          !data.some(
            (b) => b !== a && b.ndcg >= a.ndcg && b.arp <= a.arp && (b.ndcg > a.ndcg || b.arp < a.arp),
          ),
      )
      .map((r) => r.model),
  );
}

export function Results() {
  const [focus, setFocus] = useState<string>("m1");
  const front = paretoFront(rows);
  const best = Object.fromEntries(
    COLUMNS.map((c) => {
      const values = rows.map((r) => r[c.key]);
      return [c.key, c.lower ? Math.min(...values) : Math.max(...values)];
    }),
  ) as Record<Metric, number>;
  const maxima = Object.fromEntries(
    COLUMNS.map((c) => [c.key, Math.max(...rows.map((r) => r[c.key]))]),
  ) as Record<Metric, number>;
  const m2 = results.m2_test_k10.filter((r) => r.n > 0);
  return (
    <div className="space-y-8">
      <header className="rise space-y-2">
        <p className="font-mono text-xs tracking-widest text-ice">BENCHMARK · TEST · K = 10</p>
        <h1 className="text-3xl font-bold tracking-tight">Kết quả thực nghiệm</h1>
        <p className="max-w-3xl text-muted">
          Tập test, seed 42, {num(results.dataset.test_users_with_targets)} người dùng có đích trong
          danh mục; danh sách che cả train và validation. NDCG cao hơn là chính xác hơn; ARP thấp hơn
          là ít thiên về nghệ sĩ nổi tiếng hơn.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <Card glow="ice">
          <h2 className="font-semibold">Đánh đổi độ chính xác và thiên lệch phổ biến</h2>
          <p className="mb-2 text-xs text-muted">
            Đường nét đứt nối các mô hình trên biên Pareto (không mô hình nào vừa có NDCG cao hơn vừa
            có ARP thấp hơn), tính từ chính bảng dưới.
          </p>
          <Scatter front={front} focus={focus} setFocus={setFocus} />
        </Card>
        <Card>
          <h2 className="font-semibold">Hồ sơ đa chỉ số: {MODEL_NAMES[focus]}</h2>
          <p className="mb-2 text-xs text-muted">
            Chuẩn hóa min–max giữa 8 mô hình trên từng trục. Rê chuột vào điểm hoặc dòng để đổi mô
            hình; đường mờ là PureSVD để so sánh.
          </p>
          <Radar focus={focus} />
        </Card>
      </div>

      <Card className="overflow-x-auto p-0">
        <table className="w-full min-w-[820px] text-sm">
          <thead className="text-left text-xs text-muted">
            <tr className="border-b border-border">
              <th className="px-4 py-3 font-medium">Mô hình</th>
              {COLUMNS.map((c) => (
                <th key={c.key} className="px-4 py-3 font-medium">
                  {c.label}
                  {c.lower ? " ↓" : " ↑"}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.model}
                onMouseEnter={() => setFocus(row.model)}
                onFocus={() => setFocus(row.model)}
                tabIndex={0}
                className={`border-b border-border transition-colors last:border-0 hover:bg-white/5 ${
                  focus === row.model ? "bg-lilac-soft" : ""
                }`}
              >
                <td className="px-4 py-2.5 font-medium">
                  <span className="mr-2 inline-block size-2 rounded-full" style={{ background: COLORS[row.model] ?? MUTED }} />
                  {MODEL_NAMES[row.model]}
                </td>
                {COLUMNS.map((c) => {
                  const top = row[c.key] === best[c.key];
                  const bar = c.key === "ndcg" || c.key === "arp";
                  return (
                    <td key={c.key} className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        {bar && (
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/5">
                            <div
                              className={`h-full rounded-full ${c.key === "ndcg" ? "bg-ice" : "bg-blush"}`}
                              style={{ width: `${(row[c.key] / maxima[c.key]) * 100}%` }}
                            />
                          </div>
                        )}
                        <span className={`font-mono tabular-nums ${top ? "font-semibold text-mint" : ""}`}>
                          {c.format(row[c.key])}
                        </span>
                        {top && <span title="Tốt nhất cột" className="text-[12px] text-mint">★</span>}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Người dùng mới: M2 và Popularity</h2>
        <p className="max-w-3xl text-sm text-muted">
          {m2[0].users} người dùng để dành, hồ sơ gồm N nghệ sĩ đầu tiên của họ. Trên test, M2 không
          hơn Popularity về NDCG@10 nhưng đa dạng hơn (ILD cao hơn) và ít thiên về nghệ sĩ nổi tiếng
          hơn (ARP thấp hơn).
        </p>
        <Card className="overflow-x-auto p-0">
          <table className="w-full min-w-[560px] text-sm">
            <thead className="text-left text-xs text-muted">
              <tr className="border-b border-border">
                <th className="px-4 py-3 font-medium">N</th>
                <th className="px-4 py-3 font-medium">Phương pháp</th>
                {COLUMNS.filter((c) => ["ndcg", "arp", "ild", "catalog_coverage"].includes(c.key)).map(
                  (c) => (
                    <th key={c.key} className="px-4 py-3 text-right font-medium">
                      {c.label}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {m2.map((row) => (
                <tr key={`${row.n}-${row.method}`} className="border-b border-border last:border-0 hover:bg-white/5">
                  <td className="px-4 py-2.5 font-mono">{row.n}</td>
                  <td className="px-4 py-2.5">{MODEL_NAMES[row.method]}</td>
                  {COLUMNS.filter((c) => ["ndcg", "arp", "ild", "catalog_coverage"].includes(c.key)).map(
                    (c) => (
                      <td key={c.key} className="px-4 py-2.5 text-right font-mono tabular-nums">
                        {c.format(row[c.key])}
                      </td>
                    ),
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </section>

      <p className="text-xs text-muted">Nguồn: {results.sources.slice(1, 3).join(", ")}.</p>
    </div>
  );
}

function Scatter({
  front,
  focus,
  setFocus,
}: {
  front: Set<string>;
  focus: string;
  setFocus: (m: string) => void;
}) {
  const W = 520;
  const H = 300;
  const pad = { l: 52, r: 16, t: 14, b: 40 };
  const maxArp = Math.ceil(Math.max(...rows.map((r) => r.arp)) / 50) * 50;
  const maxNdcg = Math.ceil(Math.max(...rows.map((r) => r.ndcg)) * 20) / 20;
  const x = (arp: number) => pad.l + (arp / maxArp) * (W - pad.l - pad.r);
  const y = (ndcg: number) => H - pad.b - (ndcg / maxNdcg) * (H - pad.t - pad.b);
  const frontier = rows.filter((r) => front.has(r.model)).sort((a, b) => a.arp - b.arp);
  const xTicks = Array.from({ length: maxArp / 50 + 1 }, (_, i) => i * 50);
  const yTicks = Array.from({ length: Math.round(maxNdcg / 0.05) + 1 }, (_, i) => i * 0.05);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Biểu đồ NDCG@10 theo ARP">
      <rect x={pad.l} y={pad.t} width={(x(maxArp / 2) - pad.l)} height={y(maxNdcg / 2) - pad.t} fill="rgba(74,222,128,0.06)" />
      <text x={pad.l + 6} y={pad.t + 14} className="fill-mint text-[12px]">
        ARP thấp · NDCG cao
      </text>
      {xTicks.map((t) => (
        <g key={`x${t}`}>
          <line x1={x(t)} x2={x(t)} y1={pad.t} y2={H - pad.b} stroke="rgba(255,255,255,0.05)" />
          <text x={x(t)} y={H - pad.b + 14} textAnchor="middle" className="fill-[var(--muted)] font-mono text-[12px]">
            {t}
          </text>
        </g>
      ))}
      {yTicks.map((t) => (
        <g key={`y${t}`}>
          <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="rgba(255,255,255,0.05)" />
          <text x={pad.l - 6} y={y(t) + 3} textAnchor="end" className="fill-[var(--muted)] font-mono text-[12px]">
            {num(t, 2)}
          </text>
        </g>
      ))}
      <text x={(W + pad.l) / 2} y={H - 6} textAnchor="middle" className="fill-[var(--muted)] text-[13px]">
        ARP (số người nghe trung bình) → thấp hơn tốt hơn
      </text>
      <text x={12} y={(H - pad.b) / 2} textAnchor="middle" transform={`rotate(-90 12 ${(H - pad.b) / 2})`} className="fill-[var(--muted)] text-[13px]">
        NDCG@10 ↑
      </text>
      <motion.polyline
        points={frontier.map((r) => `${x(r.arp)},${y(r.ndcg)}`).join(" ")}
        fill="none"
        stroke="#4ade80"
        strokeWidth={1.5}
        strokeDasharray="5 4"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.2 }}
      />
      {rows.map((r, i) => {
        const active = focus === r.model;
        const color = COLORS[r.model] ?? MUTED;
        return (
          <g
            key={r.model}
            onMouseEnter={() => setFocus(r.model)}
            className="cursor-pointer"
            tabIndex={0}
            onFocus={() => setFocus(r.model)}
          >
            <motion.circle
              cx={x(r.arp)}
              cy={y(r.ndcg)}
              initial={false}
              animate={{ r: active ? 8 : 5.5 }}
              transition={{ delay: i * 0.02, type: "spring", stiffness: 300, damping: 18 }}
              fill={color}
              stroke={front.has(r.model) ? "white" : "none"}
              strokeWidth={1.5}
              style={{ filter: active ? `drop-shadow(0 0 6px ${color})` : undefined }}
            />
            <text
              x={x(r.arp) + LABELS[r.model].dx}
              y={y(r.ndcg) + LABELS[r.model].dy}
              textAnchor={LABELS[r.model].anchor}
              className={`text-[12px] ${active ? "fill-white" : "fill-[var(--muted)]"}`}
            >
              {MODEL_NAMES[r.model]}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function Radar({ focus }: { focus: string }) {
  const size = 260;
  const c = size / 2;
  const radius = 92;
  const scale = (row: WarmRow, axis: (typeof RADAR)[number]) => {
    const values = rows.map((r) => r[axis.key]);
    const lo = Math.min(...values);
    const hi = Math.max(...values);
    const t = hi === lo ? 1 : (row[axis.key] - lo) / (hi - lo);
    return axis.lower ? 1 - t : t;
  };
  const point = (i: number, t: number) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / RADAR.length;
    return [c + Math.cos(angle) * radius * t, c + Math.sin(angle) * radius * t] as const;
  };
  const polygon = (row: WarmRow) => RADAR.map((axis, i) => point(i, scale(row, axis)).join(",")).join(" ");
  const focusRow = rows.find((r) => r.model === focus) ?? rows[0];
  const reference = rows.find((r) => r.model === "pure_svd")!;
  const color = COLORS[focus] ?? "#4da3ff";
  return (
    <svg viewBox={`0 0 ${size} ${size}`} className="mx-auto w-full max-w-[300px]" role="img" aria-label={`Radar ${MODEL_NAMES[focus]}`}>
      {[0.25, 0.5, 0.75, 1].map((t) => (
        <polygon
          key={t}
          points={RADAR.map((_, i) => point(i, t).join(",")).join(" ")}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
        />
      ))}
      {RADAR.map((axis, i) => {
        const [lx, ly] = point(i, 1.22);
        const [ex, ey] = point(i, 1);
        return (
          <g key={axis.key}>
            <line x1={c} y1={c} x2={ex} y2={ey} stroke="rgba(255,255,255,0.08)" />
            <text x={lx} y={ly + 3} textAnchor="middle" className="fill-[var(--muted)] text-[12px]">
              {axis.label}
            </text>
          </g>
        );
      })}
      {focus !== "pure_svd" && (
        <polygon points={polygon(reference)} fill="rgba(77,163,255,0.06)" stroke="#4da3ff" strokeOpacity={0.4} strokeDasharray="3 3" />
      )}
      <motion.polygon
        initial={false}
        animate={{ points: polygon(focusRow) }}
        transition={{ type: "spring", stiffness: 120, damping: 18 }}
        fill={color}
        fillOpacity={0.18}
        stroke={color}
        strokeWidth={2}
      />
    </svg>
  );
}
