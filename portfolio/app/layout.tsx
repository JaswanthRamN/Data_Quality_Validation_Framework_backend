import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Jaswanth Ram Nagabhyrava | Data Analyst",
  description:
    "Data Analyst with 3+ years of experience building SQL pipelines, Python workflows, Power BI and Tableau dashboards, and automated reporting systems that improve operational visibility and decision-making.",
  keywords: [
    "Data Analyst",
    "Business Intelligence",
    "SQL",
    "Python",
    "Power BI",
    "Tableau",
    "Baltimore",
    "ETL",
    "Data Engineering",
    "Snowflake",
  ],
  authors: [{ name: "Jaswanth Ram Nagabhyrava" }],
  openGraph: {
    title: "Jaswanth Ram Nagabhyrava | Data Analyst",
    description:
      "Data Analyst with 3+ years of experience building SQL pipelines, Python workflows, Power BI and Tableau dashboards, and automated reporting systems.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Jaswanth Ram Nagabhyrava | Data Analyst",
    description:
      "Data Analyst specializing in SQL, Python, Power BI, Tableau, and ETL pipelines.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans bg-[#0a0a0f] text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
