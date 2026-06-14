import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div>
      <section className="bg-gradient-to-b from-indigo-50 to-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            The most trusted internship transparency platform
          </h1>
          <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
            Discover internships, read verified intern reviews, join company discussions, and make informed decisions.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/internships">
              <Button>Browse Internships</Button>
            </Link>
            <Link href="/rankings">
              <Button variant="outline">View Rankings</Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto py-16 px-4 grid md:grid-cols-3 gap-6">
        {[
          { title: "Verified Reviews", desc: "Only verified interns can submit reviews after admin verification." },
          { title: "Company Rankings", desc: "Transparent scores based on learning, mentorship, and trust metrics." },
          { title: "Community Discussions", desc: "Ask questions and share experiences on company boards." },
        ].map((f) => (
          <Card key={f.title}>
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-slate-600 text-sm">{f.desc}</p>
          </Card>
        ))}
      </section>
    </div>
  );
}
