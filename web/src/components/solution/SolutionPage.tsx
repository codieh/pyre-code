'use client';

import { useState } from 'react';
import { CodeEditor } from '@/components/workspace/CodeEditor';
import { useLocale } from '@/context/LocaleContext';
import solutionsData from '@/lib/solutions.json';

interface SolutionPageProps {
  problemId: string;
}

interface Cell {
  type: 'code' | 'markdown';
  source: string;
}

type Variant = 'interview' | 'reference';

const VARIANT_LABELS: Record<Variant, { en: string; zh: string }> = {
  interview: { en: 'Interview', zh: '面试版' },
  reference: { en: 'Reference', zh: '参考版' },
};

export function SolutionPageContent({ problemId }: SolutionPageProps) {
  const { locale } = useLocale();
  const entry = (solutionsData as Record<string, Partial<Record<Variant, Cell[]>>>)[problemId];
  const hasInterview = Boolean(entry?.interview?.length);
  const hasReference = Boolean(entry?.reference?.length);

  // Default to interview if available, otherwise reference
  const [variant, setVariant] = useState<Variant>(hasInterview ? 'interview' : 'reference');

  const cells = entry?.[variant] ?? [];

  if (!hasInterview && !hasReference) {
    return <p className="text-sm text-text-tertiary p-6">No solution available yet.</p>;
  }

  const codeCells = cells.filter((c) => c.type === 'code');
  const markdownCells = cells.filter((c) => c.type === 'markdown');
  const code = codeCells.map((c) => c.source).join('\n\n');

  return (
    <div className="grid grid-cols-2 gap-6 h-[calc(100vh-8rem)]">
      <div className="flex flex-col gap-3">
        {/* Variant toggle */}
        {hasInterview && hasReference && (
          <div className="flex rounded-lg border border-border overflow-hidden">
            {(Object.keys(VARIANT_LABELS) as Variant[]).map((v) => (
              <button
                key={v}
                onClick={() => setVariant(v)}
                className={`flex-1 px-3 py-1.5 text-xs font-medium transition-colors ${
                  variant === v
                    ? 'bg-accent text-white'
                    : 'bg-surface-secondary text-text-secondary hover:text-text-primary'
                }`}
              >
                {VARIANT_LABELS[v][locale]}
              </button>
            ))}
          </div>
        )}
        <div className="flex-1 rounded-xl border border-border overflow-hidden">
          <CodeEditor value={code} onChange={() => {}} readOnly />
        </div>
      </div>
      <div className="overflow-auto space-y-4">
        {markdownCells.map((cell, i) => (
          <div key={i} className="p-4 rounded-xl bg-surface-secondary border border-border/50">
            <pre className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
              {cell.source}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
