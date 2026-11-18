import type { Metadata } from "next";
import { JetBrains_Mono, Plus_Jakarta_Sans } from "next/font/google";
import { Nav } from "@/components/nav";
import "katex/dist/katex.min.css";
import "./globals.css";

const sans = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700", "800"],
});

const mono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: { default: "MusicRec", template: "%s · MusicRec" },
  description: "Demo hệ gợi ý nghệ sĩ âm nhạc dựa trên lọc cộng tác (Last.fm HetRec 2011).",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="vi" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans">
        <Nav />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">{children}</main>
        <footer className="border-t border-border px-4 py-6 text-center text-xs text-muted">
          Khóa luận tốt nghiệp · Dữ liệu Last.fm HetRec 2011 · Số liệu lấy từ lần chạy chính
          thức 26/10/2026
        </footer>
      </body>
    </html>
  );
}
