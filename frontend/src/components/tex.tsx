import katex from "katex";

/** Hiển thị công thức LaTeX cố định viết sẵn trong mã (không bao giờ là dữ liệu người dùng nhập). */
export function Tex({ children, block = false }: { children: string; block?: boolean }) {
  const html = katex.renderToString(children, {
    displayMode: block,
    throwOnError: false,
    strict: "ignore",
    trust: false,
  });
  return block ? (
    <div className="overflow-x-auto py-1 text-base" dangerouslySetInnerHTML={{ __html: html }} />
  ) : (
    <span dangerouslySetInnerHTML={{ __html: html }} />
  );
}
