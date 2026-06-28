import Link from "next/link";
import styles from "./ProjectCard.module.css";
import TechBadge from "./TechBadge";

export default function ProjectCard({ project }) {
  const date = new Date(project.created_at).toLocaleDateString("he-IL", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });

  const getStatusClass = (status) => {
    if (["cloning", "scanning", "analyzing", "generating"].includes(status)) {
      return styles.analyzing;
    }
    return styles[status] || styles.pending;
  };

  const statusHebrew = {
    pending: "ממתין",
    cloning: "משכפל",
    scanning: "סורק",
    analyzing: "מנתח",
    generating: "מייצר פרומפט",
    completed: "הושלם",
    failed: "נכשל"
  };

  // Collect a few top technologies
  const renderTechs = () => {
    if (!project.technologies) return null;
    const all = [];
    if (project.technologies.languages) {
      project.technologies.languages.slice(0,2).forEach(t => all.push({name: t, cat: "languages"}));
    }
    if (project.technologies.frameworks) {
      project.technologies.frameworks.slice(0,2).forEach(t => all.push({name: t, cat: "frameworks"}));
    }
    return all.map((t, i) => <TechBadge key={i} name={t.name} category={t.cat} />);
  };

  return (
    <Link href={`/projects/${project.id}`} className={styles.card}>
      <div className={styles.header}>
        <div>
          <h3 className={styles.name}>{project.name}</h3>
          <div className={styles.url}>{project.github_url.replace("https://github.com/", "")}</div>
        </div>
        <span className={`${styles.status} ${getStatusClass(project.status)}`}>
          {statusHebrew[project.status] || project.status}
        </span>
      </div>
      
      <div className={styles.techList}>
        {renderTechs()}
      </div>
      
      <div className={styles.footer}>
        <span>נוצר ב- {date}</span>
      </div>
    </Link>
  );
}
