"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Internship {
  id: number;
  title: string;
  company_name: string;
  location: string | null;
  stipend: number | null;
  mode: string;
}

export default function InternshipsPage() {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    api<Internship[]>(`/internships?q=${encodeURIComponent(q)}`)
      .then(setInternships)
      .catch(() => setInternships([]));
  }, [q]);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Internship Listings</h1>
      <input
        className="w-full max-w-md mb-6 h-10 rounded-md border border-border px-3"
        placeholder="Search internships..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <div className="grid gap-4">
        {internships.map((i) => (
          <Card key={i.id} className="flex justify-between items-center">
            <div>
              <h2 className="font-semibold">{i.title}</h2>
              <p className="text-sm text-slate-600">{i.company_name} · {i.location || "Remote"} · {i.mode}</p>
              {i.stipend && <p className="text-sm text-green-700">₹{i.stipend.toLocaleString()}/mo</p>}
            </div>
            <Link href={`/internships/${i.id}`}>
              <Button variant="outline">View</Button>
            </Link>
          </Card>
        ))}
        {internships.length === 0 && <p className="text-slate-500">No internships found.</p>}
      </div>
    </div>
  );
}
