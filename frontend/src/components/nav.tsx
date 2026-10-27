"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/nguoi-dung", label: "Người dùng có sẵn" },
  { href: "/nguoi-moi", label: "Người dùng mới" },
  { href: "/luong", label: "Luồng hoạt động" },
  { href: "/ket-qua", label: "Kết quả" },
] as const;

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-bg/70 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="grid size-7 place-items-center rounded-full bg-gradient-to-br from-ice to-lilac text-sm text-white shadow-[0_0_18px_rgba(77,163,255,0.5)]">
            ♪
          </span>
          MusicRec
        </Link>
        <div className="flex flex-wrap gap-1 text-sm">
          {LINKS.map((link) => {
            const active = pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-full px-3 py-1.5 transition-colors ${
                  active
                    ? "bg-white/10 text-text shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)]"
                    : "text-muted hover:bg-surface-2 hover:text-text"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
