import Editor from "@monaco-editor/react";

type CodeEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export function CodeEditor({ value, onChange }: CodeEditorProps) {
  return (
    <div className="editor-shell">
      <Editor
        height="100%"
        defaultLanguage="python"
        value={value}
        theme="vs-light"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
          tabSize: 4,
          scrollBeyondLastLine: false,
          automaticLayout: true
        }}
        onChange={(next) => onChange(next ?? "")}
      />
    </div>
  );
}
