"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Profile {
  name: string;
  college: string | null;
  skills: string[];
}

interface Application {
  id: number;
  internship_id: number;
  status: string;
}

interface Notification {
  id: number;
  type: string;
  payload: Record<string, unknown>;
}

export default function StudentDashboard() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    api<Profile>("/students/me").then(setProfile).catch(() => {});
    api<Application[]>("/students/applications").then(setApplications).catch(() => {});
    api<Notification[]>("/notifications").then(setNotifications).catch(() => {});
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Student Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <h2 className="font-semibold mb-3">Profile</h2>
          {profile ? (
            <>
              <p>{profile.name}</p>
              <p className="text-sm text-slate-600">{profile.college}</p>
              <div className="flex flex-wrap gap-1 mt-2">
                {profile.skills.map((s) => <span key={s} className="text-xs bg-muted px-2 py-0.5 rounded">{s}</span>)}
              </div>
            </>
          ) : <p className="text-slate-500">Login to view profile</p>}
          <Link href="/student/verify"><Button variant="outline" className="mt-4">Upload Verification</Button></Link>
        </Card>
        <Card>
          <h2 className="font-semibold mb-3">Applications</h2>
          {applications.map((a) => (
            <div key={a.id} className="text-sm py-1 flex justify-between">
              <span>Internship #{a.internship_id}</span>
              <span className="capitalize">{a.status}</span>
            </div>
          ))}
          {applications.length === 0 && <p className="text-slate-500 text-sm">No applications yet.</p>}
        </Card>
        <Card className="md:col-span-2">
          <h2 className="font-semibold mb-3">Notifications</h2>
          {notifications.map((n) => (
            <div key={n.id} className="text-sm py-1 border-b border-border last:border-0">
              <span className="font-medium">{n.type}</span>
            </div>
          ))}
          {notifications.length === 0 && <p className="text-slate-500 text-sm">No notifications.</p>}
        </Card>
      </div>
    </div>
  );
}
