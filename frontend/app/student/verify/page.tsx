"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function VerificationPage() {
  const [companyId, setCompanyId] = useState("");
  const [docType, setDocType] = useState("offer_letter");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setStatus("Uploading...");
    try {
      const { upload, s3_key } = await api<{ upload: { url: string; fields: Record<string, string> }; s3_key: string }>(
        "/students/verification/upload-url",
        { method: "POST", body: JSON.stringify({ filename: file.name, content_type: file.type, size: file.size }) }
      );
      const formData = new FormData();
      Object.entries(upload.fields).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);
      await fetch(upload.url, { method: "POST", body: formData });
      await api("/students/verification", {
        method: "POST",
        body: JSON.stringify({ company_id: Number(companyId), doc_type: docType, s3_key }),
      });
      setStatus("Submitted! Admin will review your documents.");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Upload failed");
    }
  }

  return (
    <div className="max-w-md mx-auto py-8 px-4">
      <Card>
        <h1 className="text-xl font-bold mb-4">Upload Verification Documents</h1>
        <p className="text-sm text-slate-600 mb-4">Upload your offer letter or internship certificate for admin verification.</p>
        <form onSubmit={handleUpload} className="space-y-4">
          <Input placeholder="Company ID" value={companyId} onChange={(e) => setCompanyId(e.target.value)} required />
          <select className="w-full h-10 border rounded px-3 text-sm" value={docType} onChange={(e) => setDocType(e.target.value)}>
            <option value="offer_letter">Offer Letter</option>
            <option value="certificate">Internship Certificate</option>
          </select>
          <Input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
          <Button type="submit" className="w-full">Submit for Verification</Button>
        </form>
        {status && <p className="text-sm mt-4 text-slate-600">{status}</p>}
      </Card>
    </div>
  );
}
