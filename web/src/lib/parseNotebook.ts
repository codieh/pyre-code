export interface NotebookCell {
  type: 'markdown' | 'code';
  source: string;
}

export interface ParsedNotebook {
  title: string;
  description: string;
  cells: NotebookCell[];
}

export function parseNotebook(notebookJson: string): ParsedNotebook {
  const notebook = JSON.parse(notebookJson);

  const cells: NotebookCell[] = [];
  let title = '';
  let description = '';

  for (const cell of notebook.cells || []) {
    const source = Array.isArray(cell.source)
      ? cell.source.join('')
      : cell.source || '';

    if (cell.cell_type === 'markdown') {
      // Extract title from first markdown cell (first # heading)
      if (!title) {
        const titleMatch = source.match(/^#\s+(.+)$/m);
        if (titleMatch) {
          title = titleMatch[1].replace(/^🟢\s*/, '').replace(/^🔴\s*/, '');
        }
      }

      // Collect description from beginning of first cell
      if (!description && title) {
        // Skip the title line and collect rest
        const lines = source.split('\n');
        const descLines = lines
          .filter((line: string) => !line.startsWith('#'))
          .filter((line: string) => line.trim())
          .slice(0, 5);
        if (descLines.length > 0) {
          description = descLines.join(' ').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
        }
      }

      cells.push({ type: 'markdown', source });
    } else if (cell.cell_type === 'code') {
      // Skip boilerplate cells (install, imports that are standard)
      if (
        source.includes('torch-judge') ||
        source.includes('get_ipython') ||
        source.includes('google.colab')
      ) {
        continue;
      }

      cells.push({ type: 'code', source });
    }
  }

  return {
    title: title || 'Solution',
    description: description || '',
    cells,
  };
}

export function notebookToCode(notebookJson: string): string {
  const { cells } = parseNotebook(notebookJson);

  return cells
    .filter((cell) => cell.type === 'code')
    .map((cell) => cell.source)
    .join('\n\n');
}
