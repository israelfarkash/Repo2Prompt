import styles from "./ProgressTracker.module.css";

const STEPS = [
  { id: "pending", label: "ממתין להתחלה", icon: "⏳" },
  { id: "cloning", label: "משכפל מאגר", icon: "🔗" },
  { id: "scanning", label: "סורק קבצים ומזהה טכנולוגיות", icon: "📂" },
  { id: "analyzing", label: "מנתח קוד וארכיטקטורה", icon: "🤖" },
  { id: "generating", label: "מייצר פרומפט מקיף", icon: "✨" },
  { id: "completed", label: "תהליך הושלם", icon: "✅" }
];

export default function ProgressTracker({ currentStatus }) {
  // Determine the index of the current active step
  let activeIndex = STEPS.findIndex(s => s.id === currentStatus);
  if (activeIndex === -1) {
    if (currentStatus === "failed") activeIndex = STEPS.length; // all stop
    else activeIndex = 0;
  }

  return (
    <div className={styles.tracker}>
      {STEPS.map((step, index) => {
        let stepState = "pending";
        if (index < activeIndex || currentStatus === "completed") {
          stepState = "completed";
        } else if (index === activeIndex && currentStatus !== "completed" && currentStatus !== "failed") {
          stepState = "active";
        }

        return (
          <div key={step.id} className={`${styles.step} ${styles[stepState]}`}>
            <div className={styles.iconContainer}>
              {stepState === "completed" && step.id !== "completed" ? "✅" : step.icon}
            </div>
            <div className={styles.content}>
              <div className={styles.label}>{step.label}</div>
              <div className={styles.statusText}>
                {stepState === "completed" ? "הושלם" : stepState === "active" ? "מתבצע..." : "בהמתנה"}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
