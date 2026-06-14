"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface CompanyProfile {
  name: string;
  verification_status: string;
}

interface Analytics {
  total_applications: number;
  completion_rate: number;
  ppo_rate: number;
  avg_learning: number;
}

export default function CompanyDashboard() {
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [internship, setInternship] = useState({ title: "", description: "", location: "Remote", stipend: 20000 });

  useEffect(() => {
    api<CompanyProfile>("/companies/me").then(setProfile).catch(() => {});
    api<Analytics>("/companies/analytics").then(setAnalytics).catch(() => {});
  }, []);

  async function postInternship(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api("/companies/internships", { method: "POST", body: JSON.stringify({ ...internship, mode: "remote", skills_required: ["Python"] }) });
      alert("Internship posted!");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Company Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <h2 className="font-semibold mb-2">Company Profile</h2>
          {profile ? (
            <>
              <p className="font-medium">{profile.name}</p>
              <p className="text-sm capitalize">Status: {profile.verification_status}</p>
            </>
          ) : <p className="text-slate-500">Login as company</p>}
        </Card>
        <Card>
          <h2 className="font-semibold mb-2">Analytics</h2>
          {analytics ? (
            <div className="text-sm space-y-1">
              <p>Applications: {analytics.total_applications}</p>
              <p>Completion Rate: {(analytics.completion_rate * 100).toFixed(0)}%</p>
              <p>PPO Rate: {(analytics.ppo_rate * 100).toFixed(0)}%</p>
              <p>Avg Learning: {analytics.avg_learning.toFixed(1)}/5</p>
            </div>
          ) : <p className="text-slate-500">No data</p>}
        </Card>
        <Card className="md:col-span-2">
          <h2 className="font-semibold mb-3">Post Internship</h2>
          <form onSubmit={postInternship} className="space-y-3">
            <Input placeholder="Title" value={internship.title} onChange={(e) => setInternship({ ...internship, title: e.target.value })} required />
            <textarea className="w-full border rounded p-2 text-sm" rows={3} placeholder="Description" value={internship.description} onChange={(e) => setInternship({ ...internship, description: e.target.value })} required />
            <Input placeholder="Location" value={internship.location} onChange={(e) => setInternship({ ...internship, location: e.target.value })} />
            <Input type="number" placeholder="Stipend" value={internship.stipend} onChange={(e) => setInternship({ ...internship, stipend: Number(e.target.value) })} />
            <Button type="submit">Post Internship</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
