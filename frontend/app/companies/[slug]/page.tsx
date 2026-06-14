"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";

interface Company {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  website: string | null;
  verification_status: string;
}

export default function CompanyProfilePage() {
  const params = useParams();
  const [company, setCompany] = useState<Company | null>(null);

  useEffect(() => {
    api<Company>(`/public/companies/${params.slug}`).then(setCompany).catch(() => setCompany(null));
  }, [params.slug]);

  if (!company) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <h1 className="text-3xl font-bold">{company.name}</h1>
          {company.verification_status === "verified" && (
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Verified</span>
          )}
        </div>
        <p className="text-slate-600 mb-4">{company.description}</p>
        {company.website && (
          <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-primary text-sm">
            {company.website}
          </a>
        )}
        <div className="flex gap-4 mt-6">
          <Link href={`/companies/${company.slug}/reviews`} className="text-primary text-sm font-medium">Reviews</Link>
          <Link href={`/companies/${company.slug}/discussions`} className="text-primary text-sm font-medium">Discussions</Link>
        </div>
      </Card>
    </div>
  );
}
