import { NextResponse } from 'next/server';
import problems from '@/lib/problems.json';

export async function GET() {
  // Return problem list without test code (for the list page)
  const list = problems.problems.map(({ id, title, difficulty, functionName, hint, hintZh, descriptionEn, descriptionZh }) => ({
    id, title, difficulty, functionName, hint, hintZh, descriptionEn, descriptionZh,
  }));
  return NextResponse.json({ problems: list, total: list.length });
}
