import styles from "./TechBadge.module.css";

export default function TechBadge({ name, category }) {
  // Map categories to styles
  let badgeClass = styles.default;
  if (category === "languages") badgeClass = styles.language;
  if (category === "frameworks") badgeClass = styles.framework;
  if (category === "database") badgeClass = styles.database;
  if (category === "tools") badgeClass = styles.tool;

  return (
    <span className={`${styles.badge} ${badgeClass}`}>
      {name}
    </span>
  );
}
