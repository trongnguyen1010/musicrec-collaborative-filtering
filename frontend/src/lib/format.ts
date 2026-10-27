const vi = new Intl.NumberFormat("vi-VN");

export function num(value: number, digits = 0): string {
  return new Intl.NumberFormat("vi-VN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function int(value: number): string {
  return vi.format(Math.round(value));
}

export function pct(value: number, digits = 1): string {
  return `${num(value * 100, digits)}%`;
}

export function signedPct(from: number, to: number, digits = 1): string {
  const change = (to - from) / from;
  return `${change > 0 ? "+" : ""}${num(change * 100, digits)}%`;
}

export const MODEL_NAMES: Record<string, string> = {
  random: "Random",
  popularity: "Popularity",
  user_cf: "UserCF",
  item_cf: "ItemCF",
  svd: "SVD có độ lệch",
  pure_svd: "PureSVD",
  m1: "M1 trên PureSVD",
  implicit_als: "Implicit ALS",
  m2: "M2",
};

/** Turn the API reason code into a short Vietnamese explanation. */
export function explainReason(reason: string): string {
  if (reason.startsWith("m1_")) return "Tái xếp hạng M1 từ ứng viên PureSVD";
  if (reason === "pure_svd") return "Tương đồng tiềm ẩn (PureSVD)";
  if (reason === "implicit_als") return "Tương đồng tiềm ẩn (ALS)";
  if (reason.startsWith("popular")) return "Phổ biến với mọi người dùng";
  const m2 = /^m2_cf=(\d)_content=(\d)$/.exec(reason);
  if (m2) {
    const parts = [m2[1] === "1" && "người nghe tương tự", m2[2] === "1" && "thẻ nội dung"];
    const used = parts.filter(Boolean).join(" + ");
    return used ? `M2: ${used}` : "M2: thành phần phổ biến";
  }
  return reason;
}
