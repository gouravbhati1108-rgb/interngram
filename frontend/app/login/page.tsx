"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await api<{ access_token: string; mfa_required: boolean }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (res.mfa_required) {
        setMfaRequired(true);
        return;
      }
      router.push("/student");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  async function handleMfa(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api("/auth/mfa/verify", { method: "POST", body: JSON.stringify({ code: mfaCode }) });
      router.push("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "MFA failed");
    }
  }

  return (
    <div className="max-w-md mx-auto py-16 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-6">Login</h1>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        {!mfaRequired ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Button type="submit" className="w-full">Login</Button>
          </form>
        ) : (
          <form onSubmit={handleMfa} className="space-y-4">
            <Input placeholder="MFA Code" value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} required />
            <Button type="submit" className="w-full">Verify MFA</Button>
          </form>
        )}
        <p className="text-sm text-slate-500 mt-4">
          No account? <Link href="/register" className="text-primary">Register</Link>
        </p>
      </Card>
    </div>
  );
}
