import Link from "next/link";

const links = [
  ["/dashboard", "Dashboard"],
  ["/trades", "Trades"],
  ["/metrics", "Metrics"],
  ["/import-export", "Import/Export"],
  ["/admin/users", "Admin users"],
] as const;

export function Nav() {
  return (
    <nav className="flex flex-wrap gap-2">
      {links.map(([href, label]) => (
        <Link key={href} href={href} className="rounded-md border bg-white px-3 py-1 text-sm hover:bg-slate-100">
          {label}
        </Link>
      ))}
    </nav>
  );
}
