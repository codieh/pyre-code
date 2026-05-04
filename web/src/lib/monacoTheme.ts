import type { editor } from 'monaco-editor';

export const appleLight: editor.IStandaloneThemeData = {
  base: 'vs',
  inherit: true,
  rules: [
    { token: 'comment', foreground: 'aeaeb2', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'af52de' },
    { token: 'string', foreground: '34c759' },
    { token: 'number', foreground: 'ff9500' },
    { token: 'type', foreground: '007aff' },
    { token: 'function', foreground: '007aff' },
    { token: 'variable', foreground: '1d1d1f' },
    { token: 'operator', foreground: '6e6e73' },
    { token: 'delimiter', foreground: '6e6e73' },
  ],
  colors: {
    'editor.background': '#fafafa',
    'editor.foreground': '#1d1d1f',
    'editor.lineHighlightBackground': '#f0f0f0',
    'editor.selectionBackground': '#007aff22',
    'editorLineNumber.foreground': '#c7c7cc',
    'editorLineNumber.activeForeground': '#6e6e73',
    'editor.inactiveSelectionBackground': '#007aff11',
    'editorIndentGuide.background': '#e5e5e5',
    'editorCursor.foreground': '#007aff',
  },
};
