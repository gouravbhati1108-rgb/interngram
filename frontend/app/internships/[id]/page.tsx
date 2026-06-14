"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Internship {
  id: number;
  title: string;
  description: string;
  company_name: string;
  company_id: number;
  location: string | null;
  stipend: number | null;
  skills_required: string[];
}

export default function InternshipDetailPage() {
  const params = useParams();
  const [internship, setInternship] = useState<Internship | null>(null);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    api<Internship>(`/internships/${params.id}`).then(setInternship).catch(() => setInternship(null));
  }, [params.id]);

  async function handleApply() {
    try {
      await api(`/students/applications/${params.id}`, { method: "POST" });
      setApplied(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Apply failed — login as student first");
    }
  }

  if (!internship) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-2">{internship.title}</h1>
        <p className="text-slate-600 mb-4">{internship.company_name}</p>
        <p className="mb-4">{internship.description}</p>
        {internship.stipend && <p className="font-medium mb-2">Stipend: ₹{internship.stipend.toLocaleString()}/mo</p>}
        <div className="flex flex-wrap gap-2 mb-6">
          {internship.skills_required.map((s) => (
            <span key={s} className="px-2 py-1 bg-muted rounded text-xs">{s}</span>
          ))}
        </div>
        <Button onClick={handleApply} disabled={applied}>{applied ? "Applied" : "Apply Now"}</Button>
      </Card>
    </div>
  );
}
