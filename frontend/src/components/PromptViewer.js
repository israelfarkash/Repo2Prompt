"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import styles from "./PromptViewer.module.css";

export default function PromptViewer({ promptText, onRegenerate }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(promptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([promptText], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mega-prompt.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.viewerContainer}>
      <div className={styles.toolbar}>
        <div className={styles.title}>
          <span>✨</span> הפרומפט המוכן
        </div>
        <div className={styles.actions}>
          <button className={styles.btn} onClick={onRegenerate}>
            🔄 צור מחדש
          </button>
          <button className={styles.btn} onClick={handleDownload}>
            ⬇️ הורד כקובץ
          </button>
          <button className={`${styles.btn} ${styles.primary}`} onClick={handleCopy}>
            {copied ? "✅ הועתק!" : "📋 העתק פרומפט"}
          </button>
        </div>
      </div>
      
      <div className={styles.contentWrapper}>
        <div className={styles.markdownBody}>
          <ReactMarkdown
            components={{
              code({node, inline, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} style={{ background: "rgba(255,255,255,0.1)", padding: "2px 4px", borderRadius: "4px" }} {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {promptText}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
