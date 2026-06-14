"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Post {
  id: number;
  title: string;
  body: string;
  created_at: string;
}

export default function DiscussionsPage() {
  const params = useParams();
  const [posts, setPosts] = useState<Post[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");

  useEffect(() => {
    api<Post[]>(`/discussions/company/${params.slug}`).then(setPosts).catch(() => setPosts([]));
  }, [params.slug]);

  async function createPost(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api(`/discussions/company/${params.slug}`, { method: "POST", body: JSON.stringify({ title, body }) });
      setTitle("");
      setBody("");
      const data = await api<Post[]>(`/discussions/company/${params.slug}`);
      setPosts(data);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Login required to post");
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Discussion Forum</h1>
      <Card className="mb-6">
        <form onSubmit={createPost} className="space-y-3">
          <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <textarea className="w-full border rounded p-2 text-sm" rows={3} placeholder="Share your experience..." value={body} onChange={(e) => setBody(e.target.value)} required />
          <Button type="submit">Post</Button>
        </form>
      </Card>
      <div className="space-y-4">
        {posts.map((p) => (
          <Card key={p.id}>
            <h3 className="font-semibold">{p.title}</h3>
            <p className="text-sm text-slate-600 mt-2">{p.body}</p>
          </Card>
        ))}
        {posts.length === 0 && <p className="text-slate-500">No discussions yet. Be the first!</p>}
      </div>
    </div>
  );
}
