"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState, type ReactNode } from "react";
import { ListenerBar, listenerShare, RecommendationList } from "@/components/recommendation-list";
import {
  ArtistAvatar,
  Badge,
  Card,
  Counter,
  Notice,
  Pager,
  Segmented,
  Spinner,
  Sweep,
  usePaged,
} from "@/components/ui";
import { api, type Recommendation, type RecommendResponse, type UserHistory } from "@/lib/api";
import { int, num, signedPct } from "@/lib/format";
import { m1Grid, warm } from "@/lib/results";
import { useApi } from "@/lib/use-api";

type Mode = "compare" | "als";
const K_OPTIONS = ["5", "10", "20"] as const;
const LAMBDAS = ["0.5", "0.75", "1"] as const;
const BETAS = ["0", "0.1", "0.25", "0.5"] as const;
const PINNED = { lambda: "0.75", beta: "0.5" } as const;
const ROW = 60;
const CONTROL = "h-10";

const fmt1 = (v: number) => num(v, 1);
const fmtInt = (v: number) => int(v);
const fmtPct = (v: number) => `${v > 0 ? "+" : ""}${num(v, 1)}%`;

export function ExistingUser() {
  const users = useApi("users", api.users);
  const [picked, setPicked] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [mode, setMode] = useState<Mode>("compare");
  const [k, setK] = useState<(typeof K_OPTIONS)[number]>("10");
  const [lambda, setLambda] = useState<(typeof LAMBDAS)[number]>(PINNED.lambda);
  const [beta, setBeta] = useState<(typeof BETAS)[number]>(PINNED.beta);
  const [applied, setApplied] = useState(true);
  const userId = picked ?? users.data?.[0]?.user_id ?? null;
  const known = useMemo(() => new Set(users.data?.map((u) => u.user_id)), [users.data]);
  // M1 with lambda = 1, beta = 0 keeps the PureSVD order exactly (tested in the backend).
  const point = applied ? { lambda, beta } : { lambda: "1", beta: "0" };

  const history = useApi(userId && `history:${userId}`, () => api.history(userId!, 20));
  const base = useApi(userId && mode === "compare" && `base:${userId}:${k}`, () =>
    api.recommend({ user_id: userId!, k: Number(k), model: "pure_svd" }),
  );
  const reranked = useApi(
    userId && mode === "compare" && `m1:${userId}:${k}:${point.lambda}:${point.beta}`,
    () =>
      api.recommend({
        user_id: userId!,
        k: Number(k),
        model: "m1",
        m1_lambda: Number(point.lambda),
        m1_beta: Number(point.beta),
      }),
  );
  const als = useApi(userId && mode === "als" && `als:${userId}:${k}`, () =>
    api.recommend({ user_id: userId!, k: Number(k), model: "implicit_als" }),
  );

  function choose(value: string) {
    setDraft(value);
    if (known.has(value)) setPicked(value);
  }

  function random() {
    if (!users.data?.length) return;
    const user = users.data[Math.floor(Math.random() * users.data.length)].user_id;
    setPicked(user);
    setDraft(user);
  }

  const error = users.error ?? base.error ?? reranked.error ?? als.error;
  return (
    <div className="space-y-6">
      <header className="rise space-y-2">
        <p className="font-mono text-sm tracking-widest text-ice">WARM START</p>
        <h1 className="text-3xl font-bold tracking-tight">Người dùng có sẵn</h1>
        <p className="max-w-2xl text-muted">
          So sánh danh sách của PureSVD và của M1 cho cùng một người dùng. Nghệ sĩ người đó đã nghe
          không bao giờ được gợi ý lại.
        </p>
      </header>

      {error && <Notice tone="danger">{error}</Notice>}

      <Card className="z-20 space-y-4 shadow-[0_8px_24px_rgba(0,0,0,0.35)] lg:sticky lg:top-16">
        <div className="flex flex-wrap items-end gap-x-8 gap-y-4">
        <Field label="Người dùng">
          <div className="flex gap-2">
            <input
              list="user-ids"
              value={draft || userId || ""}
              onChange={(e) => choose(e.target.value.trim())}
              aria-label="User ID"
              className={`${CONTROL} no-picker w-28 rounded-xl border border-border bg-bg/60 px-3 font-mono`}
              inputMode="numeric"
            />
            <button
              onClick={random}
              className={`${CONTROL} rounded-xl border border-border bg-white/5 px-4 text-sm hover:border-ice`}
            >
              Ngẫu nhiên
            </button>
          </div>
          <datalist id="user-ids">
            {users.data?.map((u) => (
              <option key={u.user_id} value={u.user_id}>{`${u.history_size} nghệ sĩ`}</option>
            ))}
          </datalist>
        </Field>
        <Field label="Chế độ">
          <Segmented
            label="Chế độ"
            value={mode}
            onChange={setMode}
            options={[
              { value: "compare", label: "PureSVD và M1" },
              { value: "als", label: "Implicit ALS" },
            ]}
          />
        </Field>
        <Field label="Số gợi ý K">
          <Segmented
            label="Số gợi ý K"
            value={k}
            onChange={setK}
            options={K_OPTIONS.map((value) => ({ value, label: value }))}
          />
        </Field>
        </div>
        {mode === "compare" && (
          <div className="flex flex-wrap items-end gap-x-8 gap-y-4 border-t border-border pt-4">
            <M1Inputs
              applied={applied}
              setApplied={setApplied}
              lambda={lambda}
              setLambda={setLambda}
              beta={beta}
              setBeta={setBeta}
            />
            {base.latest && reranked.latest && (
              <LiveStats base={base.latest} m1={reranked.latest} applied={applied} />
            )}
          </div>
        )}
      </Card>
      {draft && !known.has(draft) && users.data && (
        <p className="text-sm text-danger">Không có user {draft} trong tập train.</p>
      )}

      <div className="grid items-start gap-6 lg:grid-cols-[16rem_1fr]">
        <History history={history.data} loading={history.loading} />
        <div className="min-w-0 space-y-6">
          {mode === "compare" && (
            <>
              <ValidationNote applied={applied} lambda={lambda} beta={beta} />
              {(base.loading || reranked.loading) && !reranked.latest && (
                <Spinner label="Đang gợi ý" />
              )}
              {base.latest && reranked.latest && (
                <Comparison base={base.latest} m1={reranked.latest} applied={applied} />
              )}
            </>
          )}
          {mode === "als" && als.loading && !als.latest && <Spinner label="Đang gợi ý" />}
          {mode === "als" && als.latest && <AlsList data={als.latest} userId={userId ?? ""} />}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <span className="block text-sm text-muted">{label}</span>
      <div className="flex h-10 items-center">{children}</div>
    </div>
  );
}

function History({ history, loading }: { history?: UserHistory; loading: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const items = history?.items.slice(0, expanded ? 20 : 8) ?? [];
  return (
    <Card>
      <h2 className="font-semibold">Đã nghe</h2>
      {loading && <Spinner />}
      {history && (
        <>
          <p className="mb-3 text-sm text-muted">{int(history.total)} nghệ sĩ, nghe nhiều nhất trước</p>
          <ul className="space-y-2.5">
            {items.map((item) => (
              <li key={item.item_id} className="flex items-center gap-2.5">
                <ArtistAvatar name={item.name} src={item.picture_url} size={30} />
                <span className="min-w-0 flex-1 truncate">{item.name}</span>
                {item.split === "validation" && <Badge>val</Badge>}
              </li>
            ))}
          </ul>
          {history.items.length > 8 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-3 text-sm text-ice hover:underline"
            >
              {expanded ? "Thu gọn" : "Xem thêm"}
            </button>
          )}
        </>
      )}
    </Card>
  );
}

type Lambda = (typeof LAMBDAS)[number];
type Beta = (typeof BETAS)[number];

function M1Inputs(props: {
  applied: boolean;
  setApplied: (v: boolean) => void;
  lambda: Lambda;
  setLambda: (v: Lambda) => void;
  beta: Beta;
  setBeta: (v: Beta) => void;
}) {
  const { applied, setApplied, lambda, setLambda, beta, setBeta } = props;
  return (
    <>
      <Field label="M1">
        <button
          role="switch"
          aria-checked={applied}
          onClick={() => setApplied(!applied)}
          className="flex items-center gap-3 font-medium"
        >
          <span
            className={`relative h-6 w-11 rounded-full transition-colors ${applied ? "bg-mint" : "bg-white/15"}`}
          >
            <motion.span
              layout
              transition={{ type: "spring", stiffness: 500, damping: 30 }}
              className={`absolute top-0.5 size-5 rounded-full bg-white ${applied ? "right-0.5" : "left-0.5"}`}
            />
          </span>
          {applied ? "Bật" : "Tắt"}
        </button>
      </Field>
      <div className={`flex flex-wrap gap-x-8 gap-y-4 ${applied ? "" : "pointer-events-none opacity-40"}`}>
        <Field label="λ · độ liên quan">
          <Segmented
            label="lambda"
            value={lambda}
            onChange={setLambda}
            options={LAMBDAS.map((v) => ({ value: v, label: num(Number(v), 2) }))}
          />
        </Field>
        <Field label="β · phạt phổ biến">
          <Segmented
            label="beta"
            value={beta}
            onChange={setBeta}
            options={BETAS.map((v) => ({ value: v, label: num(Number(v), 2) }))}
          />
        </Field>
      </div>
    </>
  );
}

/** Compact live numbers that stay visible in the pinned toolbar. */
function LiveStats({
  base,
  m1,
  applied,
}: {
  base: RecommendResponse;
  m1: RecommendResponse;
  applied: boolean;
}) {
  const m1Ids = new Set(m1.recommendations.map((r) => r.item_id));
  const shared = base.recommendations.filter((r) => m1Ids.has(r.item_id)).length;
  const baseMean = base.mean_listeners ?? 0;
  const m1Mean = m1.mean_listeners ?? 0;
  const change = baseMean ? ((m1Mean - baseMean) / baseMean) * 100 : 0;
  return (
    <div className="ml-auto flex flex-wrap items-end gap-x-6 gap-y-3">
      <div className="space-y-1.5">
        <span className="block text-sm text-muted">Người nghe trung bình</span>
        <p className="flex h-10 items-center gap-2 text-xl font-bold">
          <span className="text-ice">
            <Counter value={baseMean} format={fmt1} />
          </span>
          <span className="text-muted">→</span>
          <span className="text-mint">
            <Counter value={m1Mean} format={fmt1} />
          </span>
          <span className={`text-base ${change < 0 ? "text-mint" : "text-muted"}`}>
            <Counter value={change} format={fmtPct} />
          </span>
        </p>
      </div>
      <div className="space-y-1.5">
        <span className="block text-sm text-muted">Chung{applied ? "" : " (M1 tắt)"}</span>
        <p className="flex h-10 items-center text-xl font-bold">
          <Counter value={shared} format={fmtInt} />
          <span className="text-base text-muted">/{base.recommendations.length}</span>
        </p>
      </div>
    </div>
  );
}

function ValidationNote({ applied, lambda, beta }: { applied: boolean; lambda: Lambda; beta: Beta }) {
  const pinned = lambda === PINNED.lambda && beta === PINNED.beta;
  const point = applied ? m1Grid(Number(lambda), Number(beta)) : m1Grid(1, 0);
  const baseGrid = m1Grid(1, 0);
  return (
    <Card className="flex flex-wrap items-center gap-3 py-4 text-sm">
      {applied && pinned && <Badge tone="mint">Cấu hình đã chọn</Badge>}
      {applied && !pinned && <Badge tone="lilac">Điểm khác trong lưới</Badge>}
      {!applied && <Badge>Như PureSVD</Badge>}
      <span className="text-muted">Validation, toàn bộ người dùng:</span>
      <Chip label="NDCG@10" value={num(point.ndcg, 4)} change={signedPct(baseGrid.ndcg, point.ndcg)} />
      <Chip label="ARP" value={num(point.arp, 1)} change={signedPct(baseGrid.arp, point.arp)} />
    </Card>
  );
}

function Chip({ label, value, change }: { label: string; value: string; change: string }) {
  return (
    <span className="rounded-lg bg-white/5 px-2.5 py-1">
      <span className="text-muted">{label} </span>
      <span className="font-mono">{value}</span>
      <span className="ml-1.5 font-mono text-muted">({change})</span>
    </span>
  );
}

function Comparison({
  base,
  m1,
  applied,
}: {
  base: RecommendResponse;
  m1: RecommendResponse;
  applied: boolean;
}) {
  const baseRank = new Map(base.recommendations.map((r) => [r.item_id, r.rank]));
  const m1Rank = new Map(m1.recommendations.map((r) => [r.item_id, r.rank]));
  const dropped = base.recommendations.filter((r) => !m1Rank.has(r.item_id));
  const max = Math.max(...[...base.recommendations, ...m1.recommendations].map((r) => r.listeners));
  const n = base.recommendations.length;
  return (
    <>
      <Card className="relative space-y-4 overflow-hidden">
        <Sweep trigger={m1.recommendations.map((r) => r.item_id).join(",")} />
        <Legend />
        <div className="overflow-x-auto">
          <div className="grid min-w-[640px] grid-cols-[1fr_80px_1fr] gap-x-3">
            <h3 className="mb-2 font-semibold text-ice">PureSVD</h3>
            <span />
            <h3 className="mb-2 font-semibold text-mint">{applied ? "M1" : "M1 tắt"}</h3>
            <Column items={base.recommendations} max={max} />
            <Connectors base={base.recommendations} m1Rank={m1Rank} n={n} />
            <Column items={m1.recommendations} max={max} baseRank={baseRank} />
          </div>
        </div>
        {dropped.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 border-t border-border pt-4 text-sm">
            <span className="text-muted">Rời khỏi top {n} khi bật M1:</span>
            {dropped.map((r) => (
              <span key={r.item_id} className="rounded-full bg-blush-soft px-2.5 py-0.5 text-blush">
                {r.name} · {int(r.listeners)} người nghe
              </span>
            ))}
          </div>
        )}
      </Card>
    </>
  );
}

function Legend() {
  return (
    <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-muted">
      <span className="flex items-center gap-2">
        <span className="h-0.5 w-6 rounded bg-mint" /> lên hạng
      </span>
      <span className="flex items-center gap-2">
        <span className="h-0.5 w-6 rounded bg-blush" /> xuống hạng
      </span>
      <span className="flex items-center gap-2">
        <span className="w-6 border-t-2 border-dashed border-blush" /> rời khỏi danh sách
      </span>
      <span className="flex items-center gap-2">
        <Badge tone="mint">mới</Badge> M1 đưa vào
      </span>
      <span>Thanh ngang: số người nghe trên train (càng dài càng phổ biến)</span>
    </div>
  );
}

function Column({
  items,
  max,
  baseRank,
}: {
  items: Recommendation[];
  max: number;
  baseRank?: Map<string, number>;
}) {
  return (
    <ol className="relative" style={{ height: items.length * ROW }}>
      <AnimatePresence initial={false}>
        {items.map((item) => {
          const before = baseRank?.get(item.item_id);
          const delta = baseRank ? (before === undefined ? null : before - item.rank) : undefined;
          return (
            <motion.li
              key={item.item_id}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0, top: (item.rank - 1) * ROW }}
              exit={{ opacity: 0, x: 16 }}
              transition={{ type: "spring", stiffness: 260, damping: 28 }}
              className="absolute inset-x-0 flex items-center gap-2.5"
              style={{ height: ROW }}
            >
              <span className="w-5 text-right font-mono text-sm tabular-nums text-muted">
                {item.rank}
              </span>
              <ArtistAvatar name={item.name} src={item.picture_url} size={32} />
              <div className="min-w-0 flex-1 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="truncate font-medium">{item.name}</span>
                  {delta !== undefined && <Delta delta={delta} />}
                </div>
                <div className="flex items-center gap-2">
                  <ListenerBar share={listenerShare(item.listeners, max)} />
                  <span className="w-12 shrink-0 text-right font-mono text-sm tabular-nums text-muted">
                    {int(item.listeners)}
                  </span>
                </div>
              </div>
            </motion.li>
          );
        })}
      </AnimatePresence>
    </ol>
  );
}

function Delta({ delta }: { delta: number | null }) {
  if (delta === null) return <Badge tone="mint">mới</Badge>;
  if (delta === 0) return null;
  return delta > 0 ? (
    <span className="shrink-0 rounded-full bg-mint-soft px-2 font-mono text-sm text-mint">▲ {delta}</span>
  ) : (
    <span className="shrink-0 rounded-full bg-blush-soft px-2 font-mono text-sm text-blush">
      ▼ {-delta}
    </span>
  );
}

/** Lines from each PureSVD rank to the same artist's M1 rank; dashed if it left the list. */
function Connectors({
  base,
  m1Rank,
  n,
}: {
  base: Recommendation[];
  m1Rank: Map<string, number>;
  n: number;
}) {
  const height = n * ROW;
  const y = (rank: number) => (rank - 0.5) * ROW;
  return (
    <svg width="80" height={height} viewBox={`0 0 80 ${height}`} aria-hidden>
      {base.map((item) => {
        const to = m1Rank.get(item.item_id);
        const from = y(item.rank);
        const end = to === undefined ? height - 4 : y(to);
        const color =
          to === undefined || to > item.rank
            ? "#f472b6"
            : to < item.rank
              ? "#4ade80"
              : "rgba(255,255,255,0.22)";
        return (
          <path
            key={item.item_id}
            d={`M0 ${from} C40 ${from}, 40 ${end}, ${to === undefined ? 60 : 80} ${end}`}
            fill="none"
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            strokeDasharray={to === undefined ? "4 4" : undefined}
          />
        );
      })}
    </svg>
  );
}

function AlsList({ data, userId }: { data: RecommendResponse; userId: string }) {
  const paged = usePaged(data.recommendations, 5, `${userId}:${data.recommendations.length}`);
  return (
    <Card glow="ice" className="relative overflow-hidden">
      <Sweep trigger={data.recommendations.map((r) => r.item_id).join(",")} />
      <h2 className="font-semibold">Implicit ALS</h2>
      <p className="mb-4 text-sm text-muted">
        Thực nghiệm mở rộng, NDCG@10 test cao nhất (
        <span className="font-mono">{num(warm("implicit_als").ndcg, 4)}</span>). Không có M1 vì M1
        đặt trên PureSVD.
      </p>
      <RecommendationList
        items={paged.visible}
        maxListeners={Math.max(...data.recommendations.map((r) => r.listeners))}
      />
      <Pager label="Trang gợi ý ALS" {...paged} />
    </Card>
  );
}
