"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";
import ProjectForm from "../components/ProjectForm";
import ProjectCard from "../components/ProjectCard";
import { getProjects } from "../lib/api";

export default function Home() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await getProjects();
        setProjects(data.projects);
      } catch (err) {
        console.error("Failed to load projects", err);
      } finally {
        setLoading(false);
      }
    }
    loadProjects();
  }, []);

  return (
    <div className={`${styles.container} animate-fade-in`}>
      <section className={styles.hero}>
        <h1 className={styles.title}>הנדסה לאחור לכל פרויקט קוד</h1>
        <p className={styles.subtitle}>
          הפוך כל מאגר ב-GitHub לפרומפט מקיף ומקצועי.
          המערכת מנתחת ארכיטקטורה, קוד וטכנולוגיות כדי לייצר הוראות בנייה מחדש לכל כלי AI.
        </p>
      </section>

      <section className={styles.formSection}>
        <ProjectForm />
      </section>

      <section className={styles.projectsSection}>
        <h2 className={styles.sectionTitle}>פרויקטים אחרונים</h2>
        
        {loading ? (
          <div className={styles.loading}>טוען פרויקטים...</div>
        ) : projects.length === 0 ? (
          <div className={styles.emptyState}>
            לא נמצאו פרויקטים עדיין. הכנס כתובת למעלה כדי להתחיל.
          </div>
        ) : (
          <div className={styles.projectsGrid}>
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
