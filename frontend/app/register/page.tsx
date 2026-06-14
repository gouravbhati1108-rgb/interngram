"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", name: "", role: "student" });
  const [error, setError] = useState("");

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/auth/register", { method: "POST", body: JSON.stringify(form) });
      await api("/auth/login", { method: "POST", body: JSON.stringify({ email: form.email, password: form.password }) });
      router.push(form.role === "company" ? "/company" : "/student");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  }

  return (
    <div className="max-w-md mx-auto py-16 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-6">Register</h1>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        <form onSubmit={handleRegister} className="space-y-4">
          <Input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <Input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input type="password" placeholder="Password (min 8 chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <select
            className="flex h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
          <Button type="submit" className="w-full">Create Account</Button>
        </form>
        <p className="text-sm text-slate-500 mt-4">
          Already have an account? <Link href="/login" className="text-primary">Login</Link>
        </p>
      </Card>
    </div>
  );
}
