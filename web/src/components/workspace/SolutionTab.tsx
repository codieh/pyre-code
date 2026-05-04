'use client';

import { useState } from 'react';
import { CodeEditor } from './CodeEditor';
import { MarkdownContent } from './MarkdownContent';
import { useLocale } from '@/context/LocaleContext';
import solutionsData from '@/lib/solutions.json';
import { getSolutionCode } from '@/lib/problemContext';

type Variant = 'interview' | 'reference';

interface Cell {
  type: string;
  source: string;
  role: string;
}

const VARIANT_LABELS: Record<Variant, { en: string; zh: string }> = {
  interview: { en: 'Interview', zh: '面试版' },
  reference: { en: 'Reference', zh: '参考版' },
};

function getCells(data: Record<string, Cell[]> | undefined, variant: Variant): Cell[] {
  if (!data) return [];
  if ('cells' in data) return (data as unknown as { cells: Cell[] }).cells;
  return data[variant]?.length ? data[variant] : data.interview ?? data.reference ?? [];
}

interface SolutionTabProps {
  problemId: string;
}

export function SolutionTab({ problemId }: SolutionTabProps) {
  const { locale, t } = useLocale();
  const entry = (solutionsData as Record<string, Record<string, Cell[]>>)[problemId];
  const hasInterview = Boolean(entry?.interview?.length);
  const hasReference = Boolean(entry?.reference?.length);
  const [variant, setVariant] = useState<Variant>(hasInterview ? 'interview' : 'reference');
  const cells = getCells(entry, variant);

  if (!hasInterview && !hasReference) {
    return <div className="p-6 text-sm text-text-tertiary">{t('noSolution')}</div>;
  }

  const solutionCode = cells
    .filter((c) => c.role === 'solution')
    .map((c) => c.source)
    .join('\n\n')
    .trim();

  const demoCode = cells
    .filter((c) => c.role === 'demo')
    .map((c) => c.source)
    .join('\n\n');

  const explanations = cells.filter((c) => c.role === 'explanation');

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      {/* Variant toggle */}
      {hasInterview && hasReference && (
        <div className="flex rounded-lg border border-border/60 overflow-hidden">
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

      {solutionCode && (
        <div className="flex flex-col gap-1">
          <p className="text-xs font-medium text-text-secondary px-1">Solution</p>
          <div className="rounded-lg overflow-hidden border border-border/50">
            <CodeEditor
              value={solutionCode}
              onChange={() => {}}
              readOnly
              height={`${Math.max(120, solutionCode.split('\n').length * 22 + 32)}px`}
              allowParentScrollOnWheel
            />
          </div>
        </div>
      )}
      {explanations.map((c, i) => (
        <MarkdownContent key={i} content={c.source} />
      ))}
      {demoCode && (
        <div className="flex flex-col gap-1">
          <p className="text-xs font-medium text-text-secondary px-1">Demo</p>
          <div className="rounded-lg overflow-hidden border border-border/50">
            <CodeEditor
              value={demoCode}
              onChange={() => {}}
              readOnly
              height={`${Math.max(80, demoCode.split('\n').length * 22 + 32)}px`}
              allowParentScrollOnWheel
            />
          </div>
        </div>
      )}
    </div>
  );
}
