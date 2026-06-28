"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import styles from "./page.module.css";
import { getProject, getProjectPrompt, regeneratePrompt } from "../../../lib/api";
import ProgressTracker from "../../../components/ProgressTracker";
import PromptViewer from "../../../components/PromptViewer";
import TechBadge from "../../../components/TechBadge";

export default function ProjectPage({ params }) {
  const unwrappedParams = use(params);
  const { id } = unwrappedParams;
  
  const [project, setProject] = useState(null);
  const [status, setStatus] = useState("pending");
  const [promptData, setPromptData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function init() {
      try {
        const data = await getProject(id);
        setProject(data);
        setStatus(data.status);
        
        if (data.status === "completed") {
          fetchPrompt();
        } else if (data.status !== "failed") {
          setupSSE();
        }
      } catch (err) {
        setError("פרויקט לא נמצא או שאירעה שגיאה.");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [id]);

  const fetchPrompt = async () => {
    try {
      const data = await getProjectPrompt(id);
      setPromptData(data);
    } catch (err) {
      console.error("Failed to fetch prompt", err);
    }
  };

  const setupSSE = () => {
    const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const evtSource = new EventSource(`${url}/api/projects/${id}/status`);
    
    evtSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      
      if (data.status === "completed") {
        evtSource.close();
        fetchPrompt();
      } else if (data.status === "failed") {
        evtSource.close();
      }
    };
    
    evtSource.onerror = () => {
      evtSource.close();
    };

    return () => evtSource.close();
  };

  const handleRegenerate = async () => {
    try {
      await regeneratePrompt(id);
      setStatus("generating");
      setPromptData(null);
      setupSSE();
    } catch (err) {
      console.error("Failed to regenerate", err);
      alert("שגיאה ביצירה מחדש.");
    }
  };

  if (loading) return <div className={styles.loading}>טוען...</div>;
  if (error || !project) return <div className={styles.errorState}>{error || "שגיאה"}</div>;

  return (
    <div className={`${styles.container} animate-fade-in`}>
      <Link href="/" className={styles.backLink}>
        <span>&rarr;</span> חזרה לראשי
      </Link>
      
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>{project.name}</h1>
          <div className={styles.url}>{project.github_url}</div>
        </div>
      </div>

      {status === "failed" && (
        <div className={styles.errorState}>
          <h3>הניתוח נכשל</h3>
          <p>{project.error_message || "שגיאה לא ידועה"}</p>
        </div>
      )}

      {status !== "completed" && status !== "failed" && (
        <ProgressTracker currentStatus={status} />
      )}

      {status === "completed" && promptData && (
        <PromptViewer 
          promptText={promptData.prompt_text} 
          onRegenerate={handleRegenerate} 
        />
      )}
    </div>
  );
}
