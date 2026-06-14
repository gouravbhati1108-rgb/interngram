"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Review {
  id: number;
  learning_score: number;
  mentorship_score: number;
  recommendation_score: number;
  text: string;
  student_name: string | null;
}

export default function ReviewsPage() {
  const params = useParams();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [eligible, setEligible] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ learning_score: 5, mentorship_score: 5, work_env_score: 5, project_quality_score: 5, recommendation_score: 5, text: "", company_id: 0, internship_id: 1 });

  useEffect(() => {
    api<Company>(`/public/companies/${params.slug}`).then((c) => {
      setForm((f) => ({ ...f, company_id: c.id }));
      api<Review[]>(`/reviews/company/${c.id}`).then(setReviews);
      api<{ eligible: boolean }>(`/reviews/eligibility/${c.id}`).then((r) => setEligible(r.eligible));
    }).catch(() => {});
  }, [params.slug]);

  interface Company { id: number; name: string }

  async function submitReview(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api("/reviews", { method: "POST", body: JSON.stringify(form) });
      setShowForm(false);
      const data = await api<Review[]>(`/reviews/company/${form.company_id}`);
      setReviews(data);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Submit failed");
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Company Reviews</h1>
      {eligible && !showForm && <Button onClick={() => setShowForm(true)} className="mb-4">Write Review</Button>}
      {showForm && (
        <Card className="mb-6">
          <form onSubmit={submitReview} className="space-y-3">
            <textarea className="w-full border rounded p-2 text-sm" rows={4} placeholder="Your review..." value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} required />
            <Input type="number" placeholder="Internship ID" value={form.internship_id} onChange={(e) => setForm({ ...form, internship_id: Number(e.target.value) })} />
            <Button type="submit">Submit Review</Button>
          </form>
        </Card>
      )}
      <div className="space-y-4">
        {reviews.map((r) => (
          <Card key={r.id}>
            <div className="flex gap-4 text-sm text-slate-500 mb-2">
              <span>Learning: {r.learning_score}/5</span>
              <span>Mentorship: {r.mentorship_score}/5</span>
              <span>Recommend: {r.recommendation_score}/5</span>
            </div>
            <p>{r.text}</p>
            {r.student_name && <p className="text-xs text-slate-400 mt-2">— {r.student_name}</p>}
          </Card>
        ))}
        {reviews.length === 0 && <p className="text-slate-500">No reviews yet.</p>}
      </div>
    </div>
  );
}
