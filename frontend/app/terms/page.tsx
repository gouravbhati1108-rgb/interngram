import { Card } from "@/components/ui/card";

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Card>
        <h1 className="text-2xl font-bold mb-4">Terms of Service</h1>
        <div className="text-sm text-slate-600 space-y-4">
          <p>By using Interngram, you agree to these terms. Interngram is a trust-based internship transparency platform for engineering students.</p>
          <h2 className="font-semibold text-foreground">User Responsibilities</h2>
          <p>Users must provide accurate information. Fake reviews, fraudulent verification documents, and abusive content are prohibited and may result in account termination.</p>
          <h2 className="font-semibold text-foreground">Review Policy</h2>
          <p>Only verified interns (with admin-approved offer letters or certificates) may submit reviews. Reviews are moderated before publication.</p>
          <h2 className="font-semibold text-foreground">Company Accounts</h2>
          <p>Companies must undergo verification before posting internships. Interngram reserves the right to remove companies that violate platform policies.</p>
          <h2 className="font-semibold text-foreground">Limitation of Liability</h2>
          <p>Interngram provides information and community features but does not guarantee internship placements. Users make independent decisions based on available data.</p>
        </div>
      </Card>
    </div>
  );
}
