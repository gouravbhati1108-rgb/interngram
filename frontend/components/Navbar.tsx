import Link from "next/link";

const nav = [
  { href: "/internships", label: "Internships" },
  { href: "/rankings", label: "Rankings" },
  { href: "/login", label: "Login" },
  { href: "/register", label: "Register" },
];

export function Navbar() {
  return (
    <header className="border-b border-border bg-white sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-xl text-primary">
          Interngram
        </Link>
        <nav className="flex gap-4 text-sm items-center">
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-primary transition-colors">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border py-8 px-4 mt-16">
      <div className="max-w-6xl mx-auto flex flex-wrap gap-4 text-sm text-slate-500">
        <Link href="/privacy" className="hover:text-primary">Privacy Policy</Link>
        <Link href="/terms" className="hover:text-primary">Terms of Service</Link>
        <Link href="/cookies" className="hover:text-primary">Cookie Policy</Link>
      </div>
    </footer>
  );
}
