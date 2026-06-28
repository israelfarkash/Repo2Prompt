<div dir="rtl">

# 🧠 Repo2Prompt

> הפוך כל פרויקט גיטהאב לפרומפט חכם (Mega-Prompt) שבעזרתו תוכל לשחזר ולבנות את הפרויקט מאפס באמצעות AI (כמו Claude, Cursor או GPT).

[English Version Below](#english-version)

![Version](https://img.shields.io/badge/version-1.0.0--mvp-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-yellow)
![Next.js](https://img.shields.io/badge/next.js-16-black)

---

## 🎯 מה המערכת עושה?

המערכת **AI Project Reverse Engineer** היא כלי אוטומטי לחלוטין שמטרתו לחקור ולהבין קוד מקור קיים, ולהפיק ממנו אפיון מדויק ל-AI. תהליך העבודה:

1. **קולטת** כתובת (URL) של מאגר GitHub פתוח.
2. **משכפלת (Cloning)** את הפרויקט בצורה מאובטחת.
3. **סורקת ומנתחת** את הקוד, הארכיטקטורה, והטכנולוגיות בעזרת מנוע **Google Gemini AI**.
4. **מייצרת פרומפט מקיף (Mega Prompt)** שניתן להעתיק ולהדביק בכלי פיתוח של AI כדי ליצור מחדש פרויקט זהה או דומה לחלוטין.

### למה זה מיוחד?
זה לא סתם כלי שמסכם קוד! האלגוריתם שלנו (היושב בשרת ה-Backend) מונחה להוציא מסמך אדריכלי מלא הכולל:
- תכנון שלבי ביצוע מפורט עבור ה-AI (Execution Plan).
- תיאור "מאחורי הקלעים" לכל פיצ'ר (איך הוא עובד, לא רק מה הוא עושה).
- זיהוי גרסאות מדויקות של טכנולוגיות, ושליפת מבנה מדויק של מסדי נתונים (Schema).

---

## 🏗️ מבנה וטכנולוגיות

המערכת בנויה משני חלקים עיקריים שרצים על המחשב שלך:

* **ממשק משתמש (Frontend)**: נבנה ב-`Next.js 16` וב-`React 19`. כולל עיצוב פרימיום בעברית (Dark Mode).
* **שרת (Backend)**: נבנה ב-`Python` עם `FastAPI`. משתמש במסד נתונים מקומי `SQLite` לשמירת נתונים, מה שאומר **שאין צורך בהתקנת שום מסד נתונים או Docker!** 

---

## 🚀 מדריך התקנה והפעלה למתחילים

הגרסה הנוכחית הותאמה כך שתרוץ בצורה הקלה ביותר ישירות על המחשב שלך.

### דרישות קדם (התקנות חובה):
אם זו פעם ראשונה שאתה מריץ קוד על המחשב, עליך להתקין את שתי התוכנות הבאות:
1. **Python**: [הורד והתקן מכאן](https://www.python.org/downloads/). 
   *⚠️ **חשוב מאוד למשתמשי Windows:** במהלך ההתקנה, חובה לסמן V בתיבה שנקראת **"Add Python to PATH"** בתחתית המסך הראשון!*
2. **Node.js**: [הורד והתקן מכאן](https://nodejs.org/en/download/). (בחר בגרסת LTS)
3. **מפתח גישה של Gemini**: [לחץ כאן כדי לייצר מפתח חינמי של גוגל (API Key)](https://aistudio.google.com/apikey).

### שלב 1: הכנת משתני הסביבה (API Key)
בתיקיית הפרויקט, צור קובץ בשם `.env` (או ערוך את הקיים) והכנס אליו את המפתח של ג'מיני שלך:
```text
GEMINI_API_KEY="AIzaSyYourApiKeyHere..."
```

### שלב 2: הפעלת שרת ה-Backend (Python)
פתח חלון טרמינל (CMD / Terminal), נווט לתיקיית הפרויקט והרץ את הפקודות הבאות לפי הסדר:
```bash
cd backend
pip install -r requirements.txt  # התקנת הספריות
uvicorn app.main:app --host 0.0.0.0 --port 8000 # הפעלת השרת
```
*השרת פועל כעת על פורט 8000.*

### שלב 3: הפעלת ה-Frontend (Next.js)
פתח **חלון טרמינל חדש**, נווט שוב לתיקיית הפרויקט והרץ:
```bash
cd frontend
npm install   # התקנת החבילות
npm run dev   # הפעלת האתר
```
*האתר פועל כעת בכתובת http://localhost:3000.*

### שלב 4: שימוש במערכת
כנס לדפדפן בכתובת **[http://localhost:3000](http://localhost:3000)**. הכנס כתובת למאגר גיטהאב (למשל: `https://github.com/facebook/react`) ולחץ על "נתח פרויקט". תראה את התקדמות הניתוח בלייב, ובסופו תקבל פרומפט מנצח!

---

</div>

---
---

<div id="english-version" dir="ltr">

# 🧠 Repo2Prompt

> Transform any GitHub repository into a comprehensive AI prompt that can rebuild the project from scratch using tools like Claude, Cursor, or GPT.

![Version](https://img.shields.io/badge/version-1.0.0--mvp-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-yellow)
![Next.js](https://img.shields.io/badge/next.js-16-black)

---

## 🎯 What Is This?

**AI Project Reverse Engineer** is an intelligent, automated tool that deeply analyzes any open-source software project and generates a perfect starting point for AI-assisted development.

1. **Accepts** a GitHub repository URL.
2. **Clones** the project locally and securely.
3. **Scans & Analyzes** architecture, patterns, technologies, and code files using **Google Gemini AI**.
4. **Generates a Mega-Prompt** — a highly detailed set of instructions that you can paste into another AI tool to **recreate the entire project**.

### Why is this special?
This is **not** a simple code summarizer. Our custom AI algorithm in the backend is designed to extract a complete "Software Architect" document that includes:
- A step-by-step **Iterative Execution Plan** for the target AI.
- "Behind the scenes" technical specifics (how features actually work, not just what they do).
- Exact version dependencies and concrete Database Schemas.

---

## 🏗️ Architecture & Technologies

The system is split into two main parts running natively on your machine:

* **Frontend**: Built with `Next.js 16` and `React 19`. Features a premium Hebrew Dark Mode UI.
* **Backend**: Built with `Python` and `FastAPI`. It uses a local `SQLite` database, meaning **no complex database setups or Docker required!**

---

## 🚀 Step-by-Step Setup Guide

This version is optimized to run locally without Docker for maximum simplicity.

### Prerequisites (Required Installations):
If you have never run code on this machine before, install these two programs:
1. **Python**: [Download & Install here](https://www.python.org/downloads/). 
   *⚠️ **CRITICAL for Windows Users:** During installation, you MUST check the box **"Add Python to PATH"** at the bottom of the very first setup screen!*
2. **Node.js**: [Download & Install here](https://nodejs.org/en/download/) (Choose the LTS version).
3. **Gemini API Key**: [Get a free Google API Key here](https://aistudio.google.com/apikey).

### Step 1: Environment Variables
Create a file named `.env` in the root project directory (or edit the existing one) and insert your API key:
```text
GEMINI_API_KEY="AIzaSyYourApiKeyHere..."
```

### Step 2: Start the Backend (Python)
Open a terminal, navigate to the project root, and run:
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
uvicorn app.main:app --host 0.0.0.0 --port 8000 # Start the server
```
*The backend is now running on port 8000.*

### Step 3: Start the Frontend (Next.js)
Open a **new terminal window**, navigate to the project root again, and run:
```bash
cd frontend
npm install   # Install dependencies
npm run dev   # Start the UI
```
*The frontend is now running on http://localhost:3000.*

### Step 4: Use the System
Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**. Paste any public GitHub URL (e.g., `https://github.com/facebook/react`) and click "Analyze". Watch the real-time progress, and copy your final Mega-Prompt!

</div>

---
<p align="center">
  Built with ❤️ using FastAPI, Next.js, and Google Gemini
</p>
