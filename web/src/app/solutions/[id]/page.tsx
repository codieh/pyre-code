import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { TopNav } from '@/components/layout/TopNav';
import { SolutionPageContent } from '@/components/solution/SolutionPage';

export default async function SolutionsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="max-w-6xl mx-auto px-6 py-6">
        <Link
          href={`/problems/${id}`}
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-accent transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to problem
        </Link>
        <SolutionPageContent problemId={id} />
      </main>
    </div>
  );
}
