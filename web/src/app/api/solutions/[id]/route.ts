import { NextResponse } from 'next/server';
import solutions from '@/lib/solutions.json';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const entry = (solutions as Record<string, Record<string, unknown[]>>)[id];
  if (!entry) {
    return NextResponse.json({ error: 'Solution not found' }, { status: 404 });
  }
  // Support both old format ({ cells }) and new format ({ reference, interview })
  if ('cells' in entry) {
    return NextResponse.json(entry);
  }
  return NextResponse.json({ variants: entry });
}
