import solutionsData from '@/lib/solutions.json';
import type { Problem } from '@/lib/types';

interface SolutionCell {
  type: string;
  source: string;
  role: string;
}

type SolutionEntry =
  | { cells: SolutionCell[] }                          // old format
  | { reference?: SolutionCell[]; interview?: SolutionCell[] }; // new format

function getCells(entry: SolutionEntry | undefined): SolutionCell[] {
  if (!entry) return [];
  if ('cells' in entry) return entry.cells;
  // Prefer interview variant
  return entry.interview?.length ? entry.interview : entry.reference ?? [];
}

export function getSolutionCode(problemId: string): string {
  const entry = (solutionsData as Record<string, SolutionEntry>)[problemId];
  const cells = getCells(entry);

  return cells
    .filter((cell) => cell.role === 'solution')
    .map((cell) => cell.source)
    .join('\n\n')
    .trim();
}

export function formatTestCode(code: string, functionName: string): string {
  return code
    .replace(/\{fn\}/g, functionName)
    .split('\n')
    .filter((line) => !line.startsWith('import ') && !line.startsWith('from '))
    .join('\n')
    .trim();
}

export function getSampleTests(problem: Problem, limit = 2): Array<{ name: string; code: string }> {
  return problem.tests.slice(0, limit).map((test) => ({
    name: test.name,
    code: formatTestCode(test.code, problem.functionName),
  }));
}
