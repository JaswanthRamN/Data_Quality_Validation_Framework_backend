"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { TrendingUp, Database, BarChart3, Building2 } from "lucide-react";

const stats = [
  { icon: TrendingUp, label: "Years Experience", value: "3+" },
  { icon: Database, label: "Records/Month Processed", value: "500K+" },
  { icon: BarChart3, label: "Reporting Time Reduced", value: "45%" },
  { icon: Building2, label: "Industries", value: "3" },
];

export default function About() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="about" className="section-padding relative">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Get to know me
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            About{" "}
            <span className="gradient-text">Me</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Text column */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <p className="text-slate-300 text-lg leading-relaxed mb-6">
              I&apos;m a Data Analyst based in Baltimore, MD, with experience
              transforming raw operational, sales, service, and inventory data
              into structured insights. My work focuses on building reliable SQL
              pipelines, automating Python-based data workflows, and creating
              dashboards in Power BI and Tableau that help teams track KPIs,
              reduce manual reporting, and make better business decisions.
            </p>
            <p className="text-slate-400 leading-relaxed">
              I enjoy solving practical business problems with clean data, clear
              dashboards, and measurable impact. Whether it&apos;s designing an
              ETL pipeline that processes half a million records a month or
              cutting a three-hour reporting process down to 20 minutes, I focus
              on work that actually moves the needle.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {["SQL", "Python", "Power BI", "Tableau", "ETL Pipelines", "Snowflake"].map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-500/10 border border-blue-500/20 text-blue-300"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Stats column */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-2 gap-4"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                className="glass-card rounded-2xl p-6 hover:bg-white/8 transition-all duration-300 group"
              >
                <stat.icon
                  size={24}
                  className="text-blue-400 mb-3 group-hover:scale-110 transition-transform"
                />
                <div className="text-3xl font-bold gradient-text mb-1">
                  {stat.value}
                </div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
