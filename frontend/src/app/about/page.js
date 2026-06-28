import Link from "next/link";
import styles from "./page.module.css";

export const metadata = {
  title: "אודות | Repo2Prompt",
};

export default function AboutPage() {
  return (
    <div className={`${styles.container} animate-fade-in`}>
      <div className={styles.card}>
        <h1 className={styles.title}>אודות המפתח</h1>
        
        <div className={styles.content}>
          <p className={styles.name}>פותח על ידי: <strong>ישראל פרקש</strong></p>
          <p className={styles.email}>
            אימייל ליצירת קשר: <a href="mailto:isralfarkash770@gmail.com">isralfarkash770@gmail.com</a>
          </p>
          
          <div className={styles.blessing}>
            יחי אדונינו מורינו ורבינו מלך המשיח לעולם ועד!
          </div>

          <div className={styles.copyrightBox}>
            <h3>זכויות יוצרים ותנאי שימוש</h3>
            <p>
              פרויקט זה נוצר ככלי עזר פתוח להנדסה לאחור של פרויקטי תוכנה. 
              מותר לשנות, לשפר ולהתאים את הקוד לצרכיך האישיים בתנאים הבאים:
            </p>
            <ul>
              <li><strong>אין לעשות שימוש מסחרי</strong> במערכת זו או בקוד שלה ללא אישור.</li>
              <li><strong>חובה להשאיר את עמוד האודות הזה (וכל הקשור אליו) בשלמותו</strong>, ללא כל שינוי, הסרה או עריכה של הפרטים.</li>
            </ul>
          </div>
        </div>

        <Link href="/" className={styles.backBtn}>
          חזרה למסך הראשי
        </Link>
      </div>
    </div>
  );
}
