'use client';

import type { ReactNode } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { PythonCode } from '@/lib/pythonHighlight';

interface MarkdownContentProps {
  content: string;
}

type Block =
  | { type: 'heading'; level: 1 | 2 | 3; content: string }
  | { type: 'list'; items: string[] }
  | { type: 'paragraph'; content: string }
  | { type: 'code'; language: string; content: string }
  | { type: 'math-block'; content: string };

function renderKatex(latex: string, displayMode: boolean): string {
  try {
    return katex.renderToString(latex, {
      displayMode,
      throwOnError: false,
      strict: false,
      trust: true,
    });
  } catch {
    return displayMode ? `$$${latex}$$` : `$${latex}$`;
  }
}

function parseBlocks(content: string): Block[] {
  const normalized = content.replace(/\r\n/g, '\n');
  const lines = normalized.split('\n');
  const blocks: Block[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      i += 1;
      continue;
    }

    // Block math: $$ ... $$ or \[ ... \]
    if (trimmed.startsWith('$$') || trimmed.startsWith('\\[')) {
      const open = trimmed.startsWith('$$') ? '$$' : '\\[';
      const close = open === '$$' ? '$$' : '\\]';
      // Single-line: $$...$$ or \[...\]
      if (trimmed.endsWith(close) && trimmed.length > open.length + close.length) {
        blocks.push({ type: 'math-block', content: trimmed.slice(open.length, -close.length) });
        i += 1;
        continue;
      }
      // Multi-line
      const mathLines: string[] = [];
      i += 1;
      while (i < lines.length) {
        const currentTrimmed = lines[i].trim();
        if (currentTrimmed.endsWith(close)) {
          const content = currentTrimmed.slice(0, -close.length);
          if (content) mathLines.push(content);
          i += 1;
          break;
        }
        mathLines.push(lines[i]);
        i += 1;
      }
      blocks.push({ type: 'math-block', content: mathLines.join('\n') });
      continue;
    }

    if (trimmed.startsWith('```')) {
      const language = trimmed.slice(3).trim().toLowerCase();
      const codeLines: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i += 1;
      }
      if (i < lines.length && lines[i].trim().startsWith('```')) {
        i += 1;
      }
      blocks.push({ type: 'code', language, content: codeLines.join('\n') });
      continue;
    }

    const headingMatch = trimmed.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      blocks.push({
        type: 'heading',
        level: headingMatch[1].length as 1 | 2 | 3,
        content: headingMatch[2].trim(),
      });
      i += 1;
      continue;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      const items: string[] = [];
      while (i < lines.length) {
        const itemLine = lines[i].trim();
        if (!/^[-*]\s+/.test(itemLine)) break;
        items.push(itemLine.replace(/^[-*]\s+/, ''));
        i += 1;
      }
      blocks.push({ type: 'list', items });
      continue;
    }

    const paragraphLines: string[] = [];
    while (i < lines.length) {
      const paragraphLine = lines[i];
      const paragraphTrimmed = paragraphLine.trim();
      if (!paragraphTrimmed) break;
      if (paragraphTrimmed.startsWith('```')) break;
      if (paragraphTrimmed.startsWith('$$')) break;
      if (paragraphTrimmed.startsWith('\\[')) break;
      if (/^(#{1,3})\s+/.test(paragraphTrimmed)) break;
      if (/^[-*]\s+/.test(paragraphTrimmed)) break;
      paragraphLines.push(paragraphLine);
      i += 1;
    }
    blocks.push({ type: 'paragraph', content: paragraphLines.join('\n').trim() });
  }

  return blocks;
}

function renderInline(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  // Match: **bold**, `code`, $$...$$ (display), $...$ (inline math), \[...\] (display), \(...\) (inline)
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\$\$[\s\S]+?\$\$|\$(?!\$)[^$\n]+?\$|\\\[[\s\S]+?\\\]|\\\([^\n]+?\\\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={`${match.index}-bold`} className="font-semibold text-text-primary">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={`${match.index}-code`}
          className="rounded bg-surface-secondary px-1.5 py-0.5 font-mono text-[0.85em] text-accent"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('$$') && token.endsWith('$$')) {
      parts.push(
        <span
          key={`${match.index}-math-block`}
          className="my-1 block overflow-x-auto"
          dangerouslySetInnerHTML={{ __html: renderKatex(token.slice(2, -2), true) }}
        />
      );
    } else if (token.startsWith('\\[') && token.endsWith('\\]')) {
      parts.push(
        <span
          key={`${match.index}-math-display`}
          className="my-1 block overflow-x-auto"
          dangerouslySetInnerHTML={{ __html: renderKatex(token.slice(2, -2), true) }}
        />
      );
    } else if (token.startsWith('\\(') && token.endsWith('\\)')) {
      parts.push(
        <span
          key={`${match.index}-math-paren`}
          dangerouslySetInnerHTML={{ __html: renderKatex(token.slice(2, -2), false) }}
        />
      );
    } else if (token.startsWith('$') && token.endsWith('$')) {
      parts.push(
        <span
          key={`${match.index}-math-inline`}
          dangerouslySetInnerHTML={{ __html: renderKatex(token.slice(1, -1), false) }}
        />
      );
    }

    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts;
}

function renderMathBlock(content: string) {
  return (
    <div
      className="overflow-x-auto py-2"
      dangerouslySetInnerHTML={{ __html: renderKatex(content, true) }}
    />
  );
}

function renderCodeBlock(language: string, content: string) {
  const isPython = language === '' || language === 'python' || language === 'py';

  return (
    <div className="overflow-hidden rounded-xl border border-border/60 bg-surface-secondary">
      {language && (
        <div className="border-b border-border/60 px-3 py-2 text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
          {language}
        </div>
      )}
      <pre className="overflow-x-auto px-4 py-3 text-xs leading-relaxed">
        {isPython ? <PythonCode code={content} /> : <code className="font-mono text-text-primary">{content}</code>}
      </pre>
    </div>
  );
}

export function MarkdownContent({ content }: MarkdownContentProps) {
  const blocks = parseBlocks(content);

  return (
    <div className="space-y-4">
      {blocks.map((block, index) => {
        if (block.type === 'heading') {
          const className =
            block.level === 1
              ? 'text-lg font-semibold text-text-primary'
              : block.level === 2
                ? 'text-base font-semibold text-text-primary'
                : 'text-sm font-semibold text-text-primary';
          return (
            <div key={index} className={className}>
              {renderInline(block.content)}
            </div>
          );
        }

        if (block.type === 'list') {
          return (
            <ul key={index} className="space-y-2 pl-5 text-sm leading-relaxed text-text-secondary">
              {block.items.map((item, itemIndex) => (
                <li key={`${index}-${itemIndex}`} className="list-disc">
                  {renderInline(item)}
                </li>
              ))}
            </ul>
          );
        }

        if (block.type === 'code') {
          return <div key={index}>{renderCodeBlock(block.language, block.content)}</div>;
        }

        if (block.type === 'math-block') {
          return <div key={index}>{renderMathBlock(block.content)}</div>;
        }

        return (
          <p key={index} className="whitespace-pre-wrap text-sm leading-relaxed text-text-secondary">
            {renderInline(block.content)}
          </p>
        );
      })}
    </div>
  );
}
