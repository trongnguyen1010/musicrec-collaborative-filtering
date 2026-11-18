import Link from "next/link";
import { int, num, signedPct } from "@/lib/format";
import { results, warm } from "@/lib/results";

const ENTRIES = [
  {
    href: "/nguoi-dung",
    title: "Người dùng có sẵn",
    body: "Chọn một trong 1.877 người dùng Last.fm, xem lịch sử nghe và so sánh danh sách PureSVD với M1.",
    tag: "PureSVD · M1 · ALS",
  },
  {
    href: "/nguoi-moi",
    title: "Người dùng mới",
    body: "Chọn 1 đến 5 nghệ sĩ bạn thích, M2 gợi ý ngay mà không cần học lại mô hình.",
    tag: "M2 · Popularity",
  },
  {
    href: "/luong",
    title: "Luồng hoạt động",
    body: "Đi qua từng bước: dữ liệu, chia tập, học mô hình, gợi ý, tái xếp hạng và kiểm tra.",
    tag: "Minh họa",
  },
] as const;

export default function Home() {
  const base = warm("pure_svd");
  const m1 = warm("m1");
  const { dataset } = results;
  return (
    <div className="space-y-10">
      <section className="rise max-w-3xl space-y-4 pt-4">
        <p className="text-sm font-medium text-ice">Demo khóa luận · Lọc cộng tác</p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Gợi ý nghệ sĩ âm nhạc, và giảm thiên lệch về nghệ sĩ nổi tiếng
        </h1>
        <p className="text-lg text-muted">
          Mô hình học từ {int(dataset.interactions)} lượt tương tác người dùng và nghệ sĩ của{" "}
          {int(dataset.users)} người dùng Last.fm. Mọi gợi ý ở đây đều do các checkpoint của lần
          chạy chính thức trả về qua API.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {ENTRIES.map((entry, index) => (
          <Link
            key={entry.href}
            href={entry.href}
            className="rise group rounded-2xl glass p-5 transition hover:-translate-y-0.5 hover:border-ice"
            style={{ animationDelay: `${80 + index * 60}ms` }}
          >
            <p className="text-xs font-medium text-muted">{entry.tag}</p>
            <h2 className="mt-2 text-lg font-semibold group-hover:text-ice">{entry.title} →</h2>
            <p className="mt-2 text-sm text-muted">{entry.body}</p>
          </Link>
        ))}
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <Fact
          value={num(base.ndcg, 4)}
          label="NDCG@10 của PureSVD trên tập test"
        />
        <Fact
          value={signedPct(base.arp, m1.arp)}
          label="Độ phổ biến trung bình (ARP) khi bật M1"
        />
        <Fact
          value={signedPct(base.ndcg, m1.ndcg)}
          label="Thay đổi NDCG@10 khi bật M1, trong ngưỡng 5% đặt trước"
        />
      </section>
      <p className="text-xs text-muted">
        Nguồn: {results.sources[1]}, seed 42, K = 10.{" "}
        <Link href="/ket-qua" className="underline">
          Xem bảng đầy đủ
        </Link>
      </p>
    </div>
  );
}

function Fact({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-2xl bg-surface-2 p-5">
      <p className="text-3xl font-bold tabular-nums">{value}</p>
      <p className="mt-1 text-sm text-muted">{label}</p>
    </div>
  );
}
