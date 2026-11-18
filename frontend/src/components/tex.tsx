import katex from "katex";

/** Render a fixed LaTeX formula written in this codebase (never user input). */
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
