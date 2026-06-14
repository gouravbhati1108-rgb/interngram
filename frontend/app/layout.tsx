import type { Metadata } from "next";
import { Navbar, Footer } from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "Interngram — Trusted Internship Platform",
  description: "Discover internships, read verified reviews, and make informed career decisions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
