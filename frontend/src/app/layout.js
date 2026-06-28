import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Header from "../components/Header";

const inter = Inter({ 
  subsets: ["latin"], 
  variable: "--font-inter",
  display: "swap" 
});

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ["latin"], 
  variable: "--font-code",
  display: "swap" 
});

export const metadata = {
  title: "Repo2Prompt | הנדסה לאחור לפרויקטים",
  description: "המרת קוד מקור ופרויקטי גיטהאב לפרומפטים חכמים",
};

export default function RootLayout({ children }) {
  return (
    <html lang="he" dir="rtl">
      <body className={`${inter.variable} ${jetbrainsMono.variable}`}>
        <Header />
        <main style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
