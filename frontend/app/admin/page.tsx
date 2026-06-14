"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface PendingItem {
  id: number;
  [key: string]: unknown;
}

export default function AdminDashboard() {
  const [companies, setCompanies] = useState<PendingItem[]>([]);
  const [verifications, setVerifications] = useState<PendingItem[]>([]);
  const [reviews, setReviews] = useState<PendingItem[]>([]);
  const [reports, setReports] = useState<PendingItem[]>([]);
  const [rankings, setRankings] = useState<PendingItem[]>([]);

  useEffect(() => {
    api<PendingItem[]>("/admin/companies/pending").then(setCompanies).catch(() => {});
    api<PendingItem[]>("/admin/verifications/pending").then(setVerifications).catch(() => {});
    api<PendingItem[]>("/admin/reviews/pending").then(setReviews).catch(() => {});
    api<PendingItem[]>("/admin/reports").then(setReports).catch(() => {});
    api<PendingItem[]>("/admin/rankings").then(setRankings).catch(() => {});
  }, []);

  async function approveCompany(id: number) {
    await api(`/admin/companies/${id}/verify`, { method: "PATCH", body: JSON.stringify({ status: "verified" }) });
    setCompanies((c) => c.filter((x) => x.id !== id));
  }

  async function approveVerification(id: number) {
    await api(`/admin/verifications/${id}`, { method: "PATCH", body: JSON.stringify({ status: "approved" }) });
    setVerifications((v) => v.filter((x) => x.id !== id));
  }

  async function approveReview(id: number) {
    await api(`/admin/reviews/${id}`, { method: "PATCH", body: JSON.stringify({ status: "approved" }) });
    setReviews((r) => r.filter((x) => x.id !== id));
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <h2 className="font-semibold mb-3">Pending Companies ({companies.length})</h2>
          {companies.map((c) => (
            <div key={c.id as number} className="flex justify-between items-center py-2 border-b text-sm">
              <span>{String(c.name)}</span>
              <Button variant="outline" onClick={() => approveCompany(c.id as number)}>Verify</Button>
            </div>
          ))}
        </Card>
        <Card>
          <h2 className="font-semibold mb-3">Pending Verifications ({verifications.length})</h2>
          {verifications.map((v) => (
            <div key={v.id as number} className="flex justify-between items-center py-2 border-b text-sm">
              <span>Doc #{v.id as number}</span>
              <Button variant="outline" onClick={() => approveVerification(v.id as number)}>Approve</Button>
            </div>
          ))}
        </Card>
        <Card>
          <h2 className="font-semibold mb-3">Review Moderation ({reviews.length})</h2>
          {reviews.map((r) => (
            <div key={r.id as number} className="py-2 border-b text-sm">
              <p className="truncate">{String(r.text)}</p>
              <Button variant="outline" className="mt-1" onClick={() => approveReview(r.id as number)}>Approve</Button>
            </div>
          ))}
        </Card>
        <Card>
          <h2 className="font-semibold mb-3">Reports ({reports.length})</h2>
          {reports.map((r) => (
            <div key={r.id as number} className="py-2 border-b text-sm">
              <p>{String(r.reason)}</p>
            </div>
          ))}
        </Card>
        <Card className="md:col-span-2">
          <h2 className="font-semibold mb-3">Ranking Monitor</h2>
          {rankings.map((r) => (
            <div key={r.company_id as number} className="flex justify-between py-1 text-sm">
              <span>Company #{r.company_id as number}</span>
              <span className="font-medium">{String(r.composite_score)}</span>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
}
