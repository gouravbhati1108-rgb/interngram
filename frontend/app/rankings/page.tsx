"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";

interface Ranking {
  company_id: number;
  company_name: string;
  company_slug: string;
  composite_score: number;
  is_provisional: boolean;
}

export default function RankingsPage() {
  const [rankings, setRankings] = useState<Ranking[]>([]);

  useEffect(() => {
    api<Ranking[]>("/rankings").then(setRankings).catch(() => setRankings([]));
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Company Rankings</h1>
      <div className="space-y-3">
        {rankings.map((r, idx) => (
          <Card key={r.company_id} className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-2xl font-bold text-slate-300 w-8">#{idx + 1}</span>
              <div>
                <Link href={`/companies/${r.company_slug}`} className="font-semibold hover:text-primary">
                  {r.company_name}
                </Link>
                {r.is_provisional && <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Provisional</span>}
              </div>
            </div>
            <span className="text-xl font-bold text-primary">{r.composite_score}</span>
          </Card>
        ))}
        {rankings.length === 0 && <p className="text-slate-500">No rankings yet.</p>}
      </div>
    </div>
  );
}
