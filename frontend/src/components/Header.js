import Link from "next/link";
import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.header}>
      <Link href="/" className={styles.logoContainer}>
        <svg 
          className={styles.logoIcon} 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span className={styles.logoText}>Repo2Prompt</span>
      </Link>
      
      <nav className={styles.nav}>
        <Link href="/" className={styles.navLink}>
          ראשי
        </Link>
        <Link href="/about" className={styles.navLink}>
          אודות
        </Link>
      </nav>
    </header>
  );
}
