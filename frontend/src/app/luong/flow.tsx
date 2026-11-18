"use client";

import { AnimatePresence, motion } from "motion/react";
import { Fragment, useEffect, useState, type ReactNode } from "react";
import { Tex } from "@/components/tex";
import { Badge, Card, Counter, Segmented } from "@/components/ui";
import { int, num, pct, signedPct } from "@/lib/format";
import { m2Row, results, warm } from "@/lib/results";

type Branch = "existing" | "new" | "empty";
interface Step {
  id: string;
  title: string;
  short: string;
  stage: "offline" | "online";
  summary: string;
  visual: ReactNode;
}

const { dataset, models, check, latency_median_ms: latency } = results;
const fmtInt = (v: number) => int(v);

function steps(branch: Branch): Step[] {
  const offline: Step[] = [
    {
      id: "data",
      title: "Dữ liệu Last.fm",
      short: "HetRec 2011",
      stage: "offline",
      summary:
        "Mỗi tương tác là số lần một người dùng nghe một nghệ sĩ. Gom lại thành ma trận người dùng × nghệ sĩ: phần lớn ô trống, và ô trống chỉ có nghĩa là chưa quan sát, không có nghĩa là không thích.",
      visual: <DataVisual />,
    },
    {
      id: "split",
      title: "Làm sạch và chia tập",
      short: "train / val / test",
      stage: "offline",
      summary:
        "Tương tác của từng người dùng được chia ngẫu nhiên theo tỉ lệ 80/10/10. Chỉ train dùng để học. Validation dùng để chọn cấu hình. Test được chấm đúng một lần, sau khi mọi cấu hình đã khóa.",
      visual: <SplitVisual />,
    },
    {
      id: "train",
      title: "Học mô hình và đóng gói",
      short: "PureSVD · M1 · M2",
      stage: "offline",
      summary:
        "PureSVD phân rã ma trận nhị phân train và giữ k thành phần lớn nhất. Cấu hình được chọn trên validation, checkpoint được khóa bằng mã băm rồi đóng gói. API chỉ nạp gói này, không học lại khi nhận yêu cầu.",
      visual: <SvdVisual />,
    },
    {
      id: "route",
      title: "Nhận yêu cầu, định tuyến",
      short: "3 nhánh",
      stage: "online",
      summary:
        "API xem yêu cầu có gì để chọn nhánh. Mỗi nhánh dùng đúng mô hình đã được đánh giá cho loại người dùng đó, và trả về nhánh đã dùng để giao diện hiển thị.",
      visual: <RouteVisual branch={branch} />,
    },
  ];
  const online: Record<Branch, Step[]> = {
    existing: [
      {
        id: "score",
        title: "Chấm điểm toàn danh mục",
        short: "top-100 ứng viên",
        stage: "online",
        summary:
          "PureSVD chấm mọi nghệ sĩ trong danh mục train cho người dùng, bỏ các nghệ sĩ người đó đã nghe ở train và validation (giống hệt khi đánh giá trên test), rồi giữ 100 ứng viên điểm cao nhất.",
        visual: <PoolVisual />,
      },
      {
        id: "m1",
        title: "Tái xếp hạng M1",
        short: `λ = ${num(models.m1.lambda, 2)} · β = ${num(models.m1.beta, 2)}`,
        stage: "online",
        summary:
          "M1 chọn lần lượt từng nghệ sĩ trong 100 ứng viên. Mỗi lượt lấy nghệ sĩ có lợi ích cao nhất: thưởng độ liên quan, phạt mức giống với các nghệ sĩ đã chọn, và phạt độ phổ biến.",
        visual: <M1Visual />,
      },
    ],
    new: [
      {
        id: "m2",
        title: "Chấm điểm M2",
        short: `α = ${num(models.m2.alpha, 2)} · T = ${models.m2.history_threshold}`,
        stage: "online",
        summary:
          "Người dùng mới chưa có trong ma trận nên không dùng được PureSVD. M2 trộn ba nguồn: ItemCF từ những người nghe cùng nghệ sĩ, độ giống thẻ nội dung, và độ phổ biến. Chọn càng nhiều nghệ sĩ, phần ItemCF càng nặng.",
        visual: <M2Visual />,
      },
    ],
    empty: [
      {
        id: "pop",
        title: "Popularity",
        short: "fallback",
        stage: "online",
        summary:
          "Không có tín hiệu cá nhân nào, nên hệ thống xếp nghệ sĩ theo mức nghe trên toàn bộ train, như mô hình nền của khóa luận, và đánh dấu kết quả là phương án dự phòng.",
        visual: <PopularityVisual />,
      },
    ],
  };
  return [
    ...offline,
    ...online[branch],
    {
      id: "return",
      title: "Trả kết quả",
      short: "JSON + kiểm chứng",
      stage: "online",
      summary:
        "API trả tên nghệ sĩ, số người nghe, lý do gợi ý và nhánh đã dùng. Chạy lại toàn bộ tập test qua chính API này cho kết quả trùng với số liệu chính thức của Chương 4.",
      visual: (
        <Facts
          items={[
            ["Người dùng có sẵn đã kiểm", int(check.warm_users)],
            ["Người dùng mới đã kiểm", int(check.m2_users)],
            ["Khớp số chính thức", check.passed ? `có, sai số ≤ ${check.tolerance}` : "không"],
            ["Trung vị API (PureSVD)", `${num(latency["POST /recommend pure_svd"], 1)} ms`],
          ]}
        />
      ),
    },
  ];
}

export function Flow() {
  const [branch, setBranch] = useState<Branch>("existing");
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(false);
  const list = steps(branch);
  const index = Math.min(active, list.length - 1);
  const offline = list.filter((s) => s.stage === "offline");
  const online = list.filter((s) => s.stage === "online");

  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(() => setActive((i) => (i + 1) % list.length), 4000);
    return () => clearInterval(timer);
  }, [playing, list.length]);

  const go = (i: number) => {
    setActive((i + list.length) % list.length);
    setPlaying(false);
  };
  const step = list[index];
  const button =
    "h-10 rounded-xl border border-border bg-white/5 px-4 text-sm transition-colors hover:border-ice";
  return (
    <div className="space-y-6">
      <header className="rise space-y-2">
        <p className="font-mono text-sm tracking-widest text-ice">PIPELINE</p>
        <h1 className="text-3xl font-bold tracking-tight">Luồng hoạt động</h1>
        <p className="max-w-2xl text-muted">
          Ba bước đầu chạy một lần khi thực nghiệm. Các bước sau chạy mỗi khi có yêu cầu gợi ý.
        </p>
      </header>

      <Card className="sticky top-16 z-20 flex flex-wrap items-center justify-between gap-4 shadow-[0_8px_24px_rgba(0,0,0,0.35)]">
        <Segmented
          label="Nhánh"
          value={branch}
          onChange={(value) => {
            setBranch(value);
            setActive(3);
          }}
          options={[
            { value: "existing", label: "Người dùng có sẵn" },
            { value: "new", label: "Người dùng mới" },
            { value: "empty", label: "Hồ sơ rỗng" },
          ]}
        />
        <div className="flex items-center gap-2">
          <button onClick={() => go(index - 1)} className={button}>
            Trước
          </button>
          <button
            onClick={() => setPlaying((p) => !p)}
            className={`${button} min-w-32 ${playing ? "border-ice text-ice" : ""}`}
          >
            {playing ? "Dừng tự chạy" : "Tự chạy"}
          </button>
          <button onClick={() => go(index + 1)} className={button}>
            Sau
          </button>
        </div>
      </Card>

      <Card className="space-y-5">
        <Lane label="OFFLINE · học và đóng gói" tone="text-ice" steps={offline} offset={0} index={index} onSelect={go} />
        <Lane
          label="ONLINE · suy luận mỗi yêu cầu"
          tone="text-mint"
          steps={online}
          offset={offline.length}
          index={index}
          onSelect={go}
        />
      </Card>

      <AnimatePresence mode="wait">
        <motion.div
          key={`${branch}-${step.id}`}
          initial={{ opacity: 0.4, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0.4, y: -10 }}
          transition={{ duration: 0.25 }}
        >
          <Card glow={step.stage === "offline" ? "ice" : "mint"} className="grid gap-8 xl:grid-cols-[1fr_1.5fr]">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Badge tone={step.stage === "offline" ? "lilac" : "mint"}>
                  {step.stage === "offline" ? "Offline · một lần" : "Online · mỗi yêu cầu"}
                </Badge>
                <span className="font-mono text-sm text-muted">
                  Bước {index + 1}/{list.length}
                </span>
              </div>
              <h2 className="text-2xl font-bold">{step.title}</h2>
              <p className="leading-relaxed text-muted">{step.summary}</p>
            </div>
            <div className="min-w-0">{step.visual}</div>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function Lane({
  label,
  tone,
  steps,
  offset,
  index,
  onSelect,
}: {
  label: string;
  tone: string;
  steps: Step[];
  offset: number;
  index: number;
  onSelect: (i: number) => void;
}) {
  return (
    <div>
      <p className={`mb-2 font-mono text-sm tracking-wide ${tone}`}>{label}</p>
      <div className="flex flex-col gap-2 md:flex-row md:items-stretch">
        {steps.map((step, i) => {
          const n = offset + i;
          const state = n < index ? "done" : n === index ? "active" : "todo";
          return (
            <Fragment key={step.id}>
              {i > 0 && <Beam lit={n <= index} />}
              <button
                onClick={() => onSelect(n)}
                aria-current={state === "active" ? "step" : undefined}
                className={`flex-1 rounded-xl border px-4 py-3 text-left transition-all duration-500 ${
                  state === "active"
                    ? "border-ice bg-ice-soft shadow-[0_0_28px_rgba(77,163,255,0.35)]"
                    : state === "done"
                      ? "border-white/15 bg-white/5"
                      : "border-border opacity-70 hover:opacity-100"
                }`}
              >
                <span className="font-mono text-sm text-muted">{n + 1}</span>
                <p className="font-semibold leading-tight">{step.title}</p>
                <p className="font-mono text-sm text-muted">{step.short}</p>
              </button>
            </Fragment>
          );
        })}
      </div>
    </div>
  );
}

/** Connector between steps: dim until reached; once reached, lit with a glowing pulse running along it. */
function Beam({ lit }: { lit: boolean }) {
  return (
    <div
      aria-hidden
      className="relative mx-auto h-6 w-0.5 shrink-0 self-center overflow-visible md:h-0.5 md:w-12"
    >
      <div className={`absolute inset-0 rounded-full ${lit ? "bg-ice" : "bg-white/12"}`} />
      {lit && <span className="pulse absolute size-2.5 rounded-full bg-white" />}
    </div>
  );
}

function Facts({ items }: { items: [string, string][] }) {
  return (
    <dl className="grid gap-3 sm:grid-cols-2">
      {items.map(([label, value]) => (
        <div key={label} className="rounded-xl bg-white/5 p-4">
          <dt className="text-sm text-muted">{label}</dt>
          <dd className="mt-1 font-mono text-lg font-semibold tabular-nums">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

/** A formula with its symbols explained underneath. */
function Formula({ tex, terms }: { tex: string; terms: [string, string][] }) {
  return (
    <div className="space-y-3 rounded-xl bg-white/5 p-4">
      <Tex block>{tex}</Tex>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm">
        {terms.map(([symbol, meaning]) => (
          <Fragment key={symbol}>
            <dt className="text-right">
              <Tex>{symbol}</Tex>
            </dt>
            <dd className="text-muted">{meaning}</dd>
          </Fragment>
        ))}
      </dl>
    </div>
  );
}

function DataVisual() {
  const density = dataset.interactions / (dataset.users * dataset.artists);
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        {(
          [
            ["Tương tác", dataset.interactions],
            ["Người dùng", dataset.users],
            ["Nghệ sĩ", dataset.artists],
          ] as const
        ).map(([label, value]) => (
          <div key={label} className="rounded-xl bg-white/5 p-4">
            <p className="text-sm text-muted">{label}</p>
            <p className="mt-1 text-xl font-semibold text-ice">
              <Counter value={value} format={fmtInt} />
            </p>
          </div>
        ))}
      </div>
      <Formula
        tex={`\\rho = \\frac{|\\mathcal{R}|}{|\\mathcal{U}| \\cdot |\\mathcal{I}|} = \\frac{${dataset.interactions}}{${dataset.users} \\times ${dataset.artists}} \\approx ${(density * 100).toFixed(2)}\\%`}
        terms={[
          ["\\mathcal{R}", "tập các cặp (người dùng, nghệ sĩ) có lượt nghe"],
          ["\\mathcal{U},\\ \\mathcal{I}", "tập người dùng và tập nghệ sĩ"],
          ["\\rho", "mật độ: tỉ lệ ô có dữ liệu trong ma trận"],
        ]}
      />
    </div>
  );
}

function SplitVisual() {
  const parts = [
    { label: "Train", value: dataset.splits.train, color: "bg-ice" },
    { label: "Validation", value: dataset.splits.validation, color: "bg-lilac" },
    { label: "Test", value: dataset.splits.test, color: "bg-mint" },
  ];
  const total = parts.reduce((sum, p) => sum + p.value, 0);
  return (
    <div className="space-y-4">
      <div className="flex h-5 gap-1 overflow-hidden rounded-full">
        {parts.map((p) => (
          <div key={p.label} className={`${p.color} h-full`} style={{ width: `${(p.value / total) * 100}%` }} />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-3">
        {parts.map((p) => (
          <div key={p.label} className="rounded-xl bg-white/5 p-4">
            <p className="flex items-center gap-2 text-sm text-muted">
              <span className={`size-2.5 rounded-full ${p.color}`} /> {p.label}
            </p>
            <p className="mt-1 font-mono text-xl font-semibold">{int(p.value)}</p>
            <p className="font-mono text-sm text-muted">{pct(p.value / total, 1)}</p>
          </div>
        ))}
      </div>
      <p className="text-sm text-muted">
        Danh mục train có <span className="font-mono text-text">{int(dataset.train_catalog_artists)}</span>{" "}
        nghệ sĩ. Nghệ sĩ chỉ xuất hiện ở validation hoặc test nằm ngoài danh mục, nên không mô hình nào
        gợi ý được.
      </p>
    </div>
  );
}

function SvdVisual() {
  const k = models.pure_svd.latent_factors;
  return (
    <div className="space-y-4">
      <Formula
        tex={`R \\approx U_k\\, \\Sigma_k\\, V_k^{\\top}, \\qquad \\hat{\\mathbf{r}}_u = \\mathbf{r}_u\\, V_k V_k^{\\top}, \\qquad k = ${k}`}
        terms={[
          ["R", `ma trận nhị phân train, ${int(dataset.train_users)} × ${int(dataset.train_catalog_artists)} (đã nghe = 1)`],
          ["U_k,\\ \\Sigma_k,\\ V_k", `k = ${k} vectơ kỳ dị lớn nhất, chọn trên validation`],
          ["\\mathbf{r}_u", "hàng của người dùng u trong R"],
          ["\\hat{\\mathbf{r}}_u", "điểm liên kết với mọi nghệ sĩ, không phải điểm đánh giá dự đoán"],
        ]}
      />
    </div>
  );
}

function RouteVisual({ branch }: { branch: Branch }) {
  const routes: [Branch, string, string][] = [
    ["existing", "Có user_id trong train", "PureSVD, có thể bật M1"],
    ["new", "Chọn 1 đến 5 nghệ sĩ", "M2"],
    ["empty", "Hồ sơ rỗng", "Popularity, đánh dấu dự phòng"],
  ];
  return (
    <div className="space-y-2.5">
      {routes.map(([id, input, output]) => (
        <motion.div
          key={id}
          animate={{ opacity: id === branch ? 1 : 0.45 }}
          className={`flex items-center gap-4 rounded-xl border p-4 ${
            id === branch ? "border-ice bg-ice-soft" : "border-border"
          }`}
        >
          <span className="flex-1">{input}</span>
          <svg width="44" height="8" aria-hidden>
            <line x1="0" y1="4" x2="44" y2="4" stroke="rgba(255,255,255,0.15)" strokeWidth="2" />
            {id === branch && <line x1="0" y1="4" x2="44" y2="4" stroke="#4da3ff" strokeWidth="3" className="beam" />}
          </svg>
          <span className="flex-1 font-medium">{output}</span>
        </motion.div>
      ))}
    </div>
  );
}

function PoolVisual() {
  const pool = models.m1.candidate_size;
  return (
    <Formula
      tex={`C_u = \\operatorname{top}_{${pool}}\\big\\{\\, \\hat{r}_{ui} : i \\in \\mathcal{I}_{\\text{train}} \\setminus H_u \\,\\big\\}`}
      terms={[
        ["\\mathcal{I}_{\\text{train}}", `danh mục train, ${int(dataset.train_catalog_artists)} nghệ sĩ`],
        ["H_u", "nghệ sĩ u đã nghe ở train và validation (bị che)"],
        ["C_u", `${pool} ứng viên đưa sang M1 (${pct(pool / dataset.train_catalog_artists, 2)} danh mục)`],
      ]}
    />
  );
}

function M1Visual() {
  const base = warm("pure_svd");
  const m1 = warm("m1");
  return (
    <div className="space-y-4">
      <Formula
        tex={`i^{*} = \\arg\\max_{i \\in C_u \\setminus S} \\Big[\\, \\lambda\\, \\operatorname{rel}(i) \\;-\\; (1-\\lambda) \\max_{j \\in S} \\operatorname{sim}(i,j) \\;-\\; \\beta\\, \\operatorname{pop}(i) \\,\\Big]`}
        terms={[
          ["S", "các nghệ sĩ đã chọn ở những lượt trước (rỗng ở lượt đầu)"],
          ["\\operatorname{rel}(i)", "điểm PureSVD chuẩn hóa min–max trên 100 ứng viên"],
          ["\\operatorname{sim}(i,j)", "cosine giữa tập người nghe (train) của hai nghệ sĩ"],
          ["\\operatorname{pop}(i)", "log(1 + số người nghe i) chia cho log(1 + số người nghe lớn nhất)"],
          ["\\lambda,\\ \\beta", `${num(models.m1.lambda, 2)} và ${num(models.m1.beta, 2)}, chọn trên validation`],
        ]}
      />
      <div className="grid grid-cols-2 gap-3">
        <TradeOff label="NDCG@10 trên test" from={base.ndcg} to={m1.ndcg} digits={4} good="up" />
        <TradeOff label="ARP trên test" from={base.arp} to={m1.arp} digits={1} good="down" />
      </div>
    </div>
  );
}

function TradeOff({
  label,
  from,
  to,
  digits,
  good,
}: {
  label: string;
  from: number;
  to: number;
  digits: number;
  good: "up" | "down";
}) {
  const better = good === "up" ? to >= from : to <= from;
  return (
    <div className="rounded-xl bg-white/5 p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 font-mono">
        {num(from, digits)} → {num(to, digits)}
      </p>
      <p className={`font-mono ${better ? "text-mint" : "text-blush"}`}>{signedPct(from, to)}</p>
    </div>
  );
}

function M2Visual() {
  const n3 = m2Row(3, "m2");
  const T = models.m2.history_threshold;
  return (
    <div className="space-y-4">
      <Formula
        tex={`s(i) = w_i\\, \\operatorname{CF}(i) + (1-w_i)\\big[\\, \\alpha\\, \\operatorname{tag}(i) + (1-\\alpha)\\, \\operatorname{pop}(i) \\,\\big], \\quad w_i = \\min\\!\\Big(1, \\frac{n}{${T}}\\Big)\\cdot \\mathbb{1}[\\operatorname{CF}\\text{ có hỗ trợ } i]`}
        terms={[
          ["n", "số nghệ sĩ người dùng đã chọn (1 đến 5)"],
          ["\\operatorname{CF}(i)", "ItemCF: độ giống của i với các nghệ sĩ đã chọn, theo người nghe chung"],
          ["\\operatorname{tag}(i)", "cosine TF-IDF thẻ nội dung; nghệ sĩ không có thẻ thì chỉ còn pop(i)"],
          ["\\alpha", `${num(models.m2.alpha, 2)}, chọn trên validation`],
        ]}
      />
      <Facts
        items={[
          ["NDCG@10 test, 3 nghệ sĩ", num(n3.ndcg, 4)],
          ["ILD test, 3 nghệ sĩ", num(n3.ild, 3)],
        ]}
      />
    </div>
  );
}

function PopularityVisual() {
  return (
    <div className="space-y-4">
      <Formula
        tex={`\\operatorname{pop}(i) = \\sum_{u \\in \\mathcal{U}} \\log_2\\!\\big(1 + c_{ui}\\big)`}
        terms={[
          ["c_{ui}", "số lần người dùng u nghe nghệ sĩ i trên train (0 nếu chưa nghe)"],
        ]}
      />
      <Facts
        items={[
          ["NDCG@10 test", num(warm("popularity").ndcg, 4)],
          ["ARP test", num(warm("popularity").arp, 1)],
        ]}
      />
    </div>
  );
}
