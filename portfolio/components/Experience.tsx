"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { MapPin, Calendar, Briefcase } from "lucide-react";

const experiences = [
  {
    title: "Data Analyst",
    company: "Rishi Inc",
    location: "Baltimore, United States",
    period: "Mar 2024 – Present",
    current: true,
    bullets: [
      "Built and maintained Power BI dashboards tracking operational and sales performance metrics, reducing manual reporting work by 45%.",
      "Designed SQL pipelines integrating Salesforce, ERP systems, and internal operational datasets processing 500K+ records per month, improving reporting accuracy by 30%.",
      "Developed Python-based ETL workflows to clean, validate, and transform datasets used in reporting and analytics pipelines.",
      "Implemented automated refresh pipelines with data quality checks and scheduled workflows, improving reliability of internal dashboards.",
      "Performed ad-hoc analyses to investigate cost patterns and operational performance metrics, providing insights used for internal decision-making.",
    ],
  },
  {
    title: "Data Analyst",
    company: "Pioneer Auto World Pvt Ltd",
    location: "Guntur, India",
    period: "Aug 2021 – Dec 2022",
    current: false,
    bullets: [
      "Consolidated sales, service, and inventory datasets across three branches, building SQL and Excel pipelines that reduced daily reporting preparation by 60%.",
      "Developed Tableau dashboards to monitor technician productivity, service throughput, and inventory turnover, improving operational visibility by 40%.",
      "Applied time-series forecasting techniques to analyze parts demand and service volume, improving workforce and inventory planning accuracy by 25%.",
      "Automated monthly operational reporting using SQL queries and Excel macros, reducing reporting preparation from 3 hours to 20 minutes.",
      "Delivered analysis supporting procurement planning decisions, contributing to $28K in quarterly cost savings.",
    ],
  },
  {
    title: "Data Analyst Intern",
    company: "Pioneer Auto World Pvt Ltd",
    location: "Guntur, India",
    period: "Jun 2020 – Jul 2021",
    current: false,
    bullets: [
      "Cleaned and validated multi-branch operational datasets using SQL, Excel, and Google Sheets for internal reporting workflows.",
      "Built Excel pivot-based dashboards to track technician performance and service completion rates.",
      "Assisted in demand and preventive maintenance analysis that improved on-time service completion by 15%.",
    ],
  },
];

export default function Experience() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="experience" className="section-padding relative">
      <div className="max-w-4xl mx-auto">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-3">
            My career
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            Work{" "}
            <span className="gradient-text">Experience</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="relative">
          {/* Timeline vertical line */}
          <motion.div
            initial={{ scaleY: 0 }}
            animate={isInView ? { scaleY: 1 } : {}}
            transition={{ duration: 1.2, delay: 0.3, ease: "easeInOut" }}
            className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-blue-500 via-purple-500 to-transparent origin-top"
          />

          <div className="space-y-10">
            {experiences.map((exp, index) => (
              <motion.div
                key={`${exp.company}-${exp.period}`}
                initial={{ opacity: 0, x: -20 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.2 }}
                className="relative pl-16"
              >
                {/* Timeline dot */}
                <div
                  className={`absolute left-3.5 top-5 w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    exp.current
                      ? "border-blue-400 bg-blue-500/20"
                      : "border-slate-600 bg-[#0a0a0f]"
                  }`}
                >
                  {exp.current && (
                    <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  )}
                </div>

                <div className="glass-card rounded-2xl p-6 hover:bg-white/6 transition-all duration-300">
                  {/* Header */}
                  <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Briefcase size={15} className="text-blue-400" />
                        <h3 className="text-lg font-bold text-white">
                          {exp.title}
                        </h3>
                      </div>
                      <div className="text-blue-300 font-semibold">
                        {exp.company}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1 text-sm text-slate-400">
                      <span className="flex items-center gap-1">
                        <Calendar size={13} />
                        {exp.period}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin size={13} />
                        {exp.location}
                      </span>
                    </div>
                  </div>

                  {/* Current badge */}
                  {exp.current && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 border border-green-500/20 text-green-400 mb-4">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                      Current Role
                    </span>
                  )}

                  {/* Bullets */}
                  <ul className="space-y-2.5">
                    {exp.bullets.map((bullet, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2.5 text-slate-300 text-sm leading-relaxed"
                      >
                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" />
                        {bullet}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
