"use client";

import { useEffect, useRef } from "react";
import { EditorState, Extension } from "@codemirror/state";
import { EditorView, keymap, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { syntaxHighlighting, defaultHighlightStyle } from "@codemirror/language";
import { oneDark } from "@codemirror/theme-one-dark";

interface CompilationError {
  line: number;
  column: number;
  message: string;
  severity: "error" | "warning";
}

interface LeanEditorProps {
  value: string;
  onChange?: (value: string) => void;
  errors?: CompilationError[];
  readOnly?: boolean;
  height?: string;
}

// Lean 4 syntax highlighting using generic highlighting
// In production, you'd want to build a proper Lezer grammar
function createLean4Highlight(): Extension {
  return syntaxHighlighting(defaultHighlightStyle);
}

// Theme matching LeanProve design system
const leanTheme = EditorView.theme(
  {
    "&": {
      backgroundColor: "#0D1117",
      color: "#C9D1D9",
      height: "100%",
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      fontSize: "14px",
      lineHeight: "1.6",
    },
    ".cm-content": {
      padding: "16px 0",
      caretColor: "#6366F1",
    },
    ".cm-focused": {
      outline: "none",
    },
    ".cm-editor.cm-focused": {
      outline: "none",
    },
    ".cm-scroller": {
      overflow: "auto",
      fontFamily: "inherit",
    },
    ".cm-gutters": {
      backgroundColor: "#0D1117",
      color: "#484F58",
      border: "none",
      borderRight: "1px solid #21262D",
      paddingRight: "8px",
    },
    ".cm-lineNumbers .cm-gutterElement": {
      padding: "0 8px 0 4px",
      minWidth: "32px",
    },
    ".cm-activeLine": {
      backgroundColor: "#161B22",
    },
    ".cm-activeLineGutter": {
      backgroundColor: "#161B22",
      color: "#6366F1",
    },
    ".cm-selectionBackground": {
      backgroundColor: "#264F78 !important",
    },
    "&.cm-focused .cm-cursor": {
      borderLeftColor: "#6366F1",
      borderLeftWidth: "2px",
    },
    // Lean keyword highlighting
    ".cm-keyword": { color: "#FF7B72" },
    ".cm-def": { color: "#D2A8FF" },
    ".cm-variable": { color: "#79C0FF" },
    ".cm-string": { color: "#A5D6FF" },
    ".cm-comment": { color: "#8B949E", fontStyle: "italic" },
    ".cm-type": { color: "#FFA657" },
    ".cm-number": { color: "#79C0FF" },
    ".cm-operator": { color: "#FF7B72" },
    // Error underline
    ".cm-diagnostic-error": {
      textDecoration: "underline wavy #EF4444",
    },
    ".cm-diagnostic-warning": {
      textDecoration: "underline wavy #F59E0B",
    },
    // Tooltip
    ".cm-tooltip": {
      backgroundColor: "#1E293B",
      border: "1px solid #334155",
      borderRadius: "8px",
      color: "#F8FAFC",
      fontSize: "12px",
    },
  },
  { dark: true }
);

export function LeanEditor({
  value,
  onChange,
  errors = [],
  readOnly = false,
  height = "100%",
}: LeanEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    if (!editorRef.current) return;

    const extensions: Extension[] = [
      lineNumbers(),
      history(),
      highlightActiveLine(),
      keymap.of([...defaultKeymap, ...historyKeymap]),
      leanTheme,
      createLean4Highlight(),
      EditorView.lineWrapping,
    ];

    if (!readOnly) {
      extensions.push(
        EditorView.updateListener.of((update) => {
          if (update.docChanged && onChangeRef.current) {
            onChangeRef.current(update.state.doc.toString());
          }
        })
      );
    } else {
      extensions.push(EditorState.readOnly.of(true));
    }

    const state = EditorState.create({
      doc: value,
      extensions,
    });

    const view = new EditorView({
      state,
      parent: editorRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update content when value changes externally
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const currentContent = view.state.doc.toString();
    if (currentContent !== value) {
      view.dispatch({
        changes: {
          from: 0,
          to: currentContent.length,
          insert: value,
        },
      });
    }
  }, [value]);

  return (
    <div
      ref={editorRef}
      style={{ height }}
      className="overflow-hidden"
    />
  );
}
