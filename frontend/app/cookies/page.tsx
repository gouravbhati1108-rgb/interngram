import { Card } from "@/components/ui/card";

export default function CookiesPage() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-4">Cookie Policy</h1>
        <div className="text-sm text-slate-600 space-y-4">
          <p>Interngram uses cookies to provide authentication and security features.</p>
          <h2 className="font-semibold text-foreground">Essential Cookies</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>access_token</strong> — JWT access token for authenticated sessions (httpOnly, 15 min)</li>
            <li><strong>refresh_token</strong> — Session refresh token (httpOnly, 7 days)</li>
            <li><strong>csrf_token</strong> — CSRF protection for mutating requests</li>
          </ul>
          <h2 className="font-semibold text-foreground">Managing Cookies</h2>
          <p>Essential cookies cannot be disabled as they are required for platform functionality. You may clear cookies by logging out or clearing browser data.</p>
        </div>
      </Card>
    </div>
  );
}
