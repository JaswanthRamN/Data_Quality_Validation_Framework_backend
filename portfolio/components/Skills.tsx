"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import {
  Database,
  BarChart3,
  Workflow,
  Cloud,
  TrendingUp,
  Wrench,
} from "lucide-react";

const skillCategories = [
  {
    icon: Database,
    title: "Data Analysis",
    color: "blue",
    skills: [
      "SQL",
      "Python",
      "Pandas",
      "NumPy",
      "Exploratory Data Analysis",
      "Data Cleaning",
      "Data Validation",
    ],
  },
  {
    icon: BarChart3,
    title: "Business Intelligence & Reporting",
    color: "cyan",
    skills: [
      "Power BI",
      "Tableau",
      "KPI Tracking",
      "Dashboard Development",
      "Executive Reporting",
      "Advanced Excel",
    ],
  },
  {
    icon: Workflow,
    title: "Data Engineering & Automation",
    color: "purple",
    skills: [
      "ETL/ELT Pipelines",
      "dbt",
      "Apache Airflow",
      "SQL Automation",
      "Python Data Workflows",
      "Data Quality Checks",
    ],
  },
  {
    icon: Cloud,
    title: "Databases & Cloud",
    color: "green",
    skills: [
      "Snowflake",
      "Redshift",
      "PostgreSQL",
      "SQL Server",
      "MySQL",
      "AWS S3",
      "AWS Lambda",
    ],
  },
  {
    icon: TrendingUp,
    title: "Statistics & Analytics",
    color: "orange",
    skills: [
      "Time Series Forecasting",
      "Regression Analysis",
      "Hypothesis Testing",
      "A/B Testing",
    ],
  },
  {
    icon: Wrench,
    title: "Tools & Systems",
    color: "pink",
    skills: ["Git", "Docker", "Jira", "ERP Systems", "SAP", "NetSuite", "Salesforce"],
  },
];

const colorMap: Record<string, { badge: string; icon: string; border: string }> = {
  blue: {
    badge: "bg-blue-500/10 text-blue-300 border-blue-500/20",
    icon: "text-blue-400",
    border: "hover:border-blue-500/30",
  },
  cyan: {
    badge: "bg-cyan-500/10 text-cyan-300 border-cyan-500/20",
    icon: "text-cyan-400",
    border: "hover:border-cyan-500/30",
  },
  purple: {
    badge: "bg-purple-500/10 text-purple-300 border-purple-500/20",
    icon: "text-purple-400",
    border: "hover:border-purple-500/30",
  },
  green: {
    badge: "bg-green-500/10 text-green-300 border-green-500/20",
    icon: "text-green-400",
    border: "hover:border-green-500/30",
  },
  orange: {
    badge: "bg-orange-500/10 text-orange-300 border-orange-500/20",
    icon: "text-orange-400",
    border: "hover:border-orange-500/30",
  },
  pink: {
    badge: "bg-pink-500/10 text-pink-300 border-pink-500/20",
    icon: "text-pink-400",
    border: "hover:border-pink-500/30",
  },
};

export default function Skills() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="skills" className="section-padding relative">
      {/* Subtle background accent */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-950/10 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto relative">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-3">
            What I work with
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            Technical{" "}
            <span className="gradient-text">Skills</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {skillCategories.map((category, index) => {
            const colors = colorMap[category.color];
            return (
              <motion.div
                key={category.title}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.1 + index * 0.08 }}
                className={`glass-card rounded-2xl p-6 transition-all duration-300 ${colors.border} hover:bg-white/6 group`}
              >
                <div className="flex items-center gap-3 mb-5">
                  <div className="p-2.5 rounded-xl bg-white/5">
                    <category.icon
                      size={20}
                      className={`${colors.icon} group-hover:scale-110 transition-transform`}
                    />
                  </div>
                  <h3 className="font-semibold text-white text-sm leading-tight">
                    {category.title}
                  </h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {category.skills.map((skill) => (
                    <span
                      key={skill}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${colors.badge}`}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
