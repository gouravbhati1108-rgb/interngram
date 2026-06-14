import { Card } from "@/components/ui/card";

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-4">Privacy Policy</h1>
        <div className="prose text-sm text-slate-600 space-y-4">
          <p>Interngram (&quot;we&quot;) is committed to protecting your personal data in accordance with applicable data protection laws, including the Digital Personal Data Protection Act, 2023 (India).</p>
          <h2 className="font-semibold text-foreground">Data We Collect</h2>
          <p>We collect account information (email, name), profile data (college, skills, resume), verification documents (offer letters, certificates), and usage data (applications, reviews, discussions).</p>
          <h2 className="font-semibold text-foreground">How We Use Data</h2>
          <p>Data is used to provide internship discovery, verified reviews, company rankings, and community features. Verification documents are reviewed by admins and stored securely in encrypted S3 storage.</p>
          <h2 className="font-semibold text-foreground">Your Rights</h2>
          <p>You may request access, correction, or deletion of your personal data by contacting privacy@interngram.com.</p>
          <h2 className="font-semibold text-foreground">Data Retention</h2>
          <p>Account data is retained while your account is active. Verification documents are retained for audit purposes for up to 3 years.</p>
        </div>
      </Card>
    </div>
  );
}
