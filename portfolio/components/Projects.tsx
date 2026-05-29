"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Github, ExternalLink, BookOpen, Zap } from "lucide-react";

const projects = [
  {
    title: "Off-Task Behavior Prediction – ML & Dashboards",
    description:
      "Analyzed 27K+ behavioral records and trained classification models to predict off-task behavior patterns. Built a Flask-based application with dashboards to visualize predictions and behavioral trends.",
    tech: ["Python", "Machine Learning", "Flask", "Dashboards", "Data Visualization"],
    impact: "Improved model F1-score by 12% and helped reduce manual behavior analysis effort.",
    impactColor: "blue",
    gradient: "from-blue-600/20 to-purple-600/20",
    borderHover: "hover:border-blue-500/40",
  },
  {
    title: "Baltimore Crime Analysis – SQL, Python & Tableau",
    description:
      "Analyzed 1M+ emergency call records to identify geographic and temporal crime trends using SQL and Python. Built interactive Tableau dashboards and automated weekly reporting.",
    tech: ["SQL", "Python", "Tableau", "Data Cleaning", "Geospatial Analysis"],
    impact: "Reduced manual report generation time by 90% and supported data-driven resource allocation.",
    impactColor: "cyan",
    gradient: "from-cyan-600/20 to-blue-600/20",
    borderHover: "hover:border-cyan-500/40",
  },
  {
    title: "Formula 1 Lap Time Prediction – FastF1 & ML",
    description:
      "Built a regression model using Formula 1 telemetry data and engineered racing features to predict lap times across drivers and sessions.",
    tech: ["Python", "FastF1", "Pandas", "Scikit-learn", "Machine Learning"],
    impact: "Achieved 93% R² and 0.42 MAE, reducing analysis turnaround time from 30 minutes to under 5 minutes per session.",
    impactColor: "purple",
    gradient: "from-purple-600/20 to-pink-600/20",
    borderHover: "hover:border-purple-500/40",
  },
];

const techColorMap: Record<string, string> = {
  Python: "bg-blue-500/10 text-blue-300 border-blue-500/20",
  SQL: "bg-cyan-500/10 text-cyan-300 border-cyan-500/20",
  "Machine Learning": "bg-purple-500/10 text-purple-300 border-purple-500/20",
  Flask: "bg-green-500/10 text-green-300 border-green-500/20",
  Tableau: "bg-orange-500/10 text-orange-300 border-orange-500/20",
  FastF1: "bg-red-500/10 text-red-300 border-red-500/20",
  Pandas: "bg-blue-500/10 text-blue-300 border-blue-500/20",
  "Scikit-learn": "bg-yellow-500/10 text-yellow-300 border-yellow-500/20",
};

const defaultTechColor = "bg-slate-500/10 text-slate-300 border-slate-500/20";

const impactColorMap: Record<string, string> = {
  blue: "bg-blue-500/10 border-blue-500/20 text-blue-300",
  cyan: "bg-cyan-500/10 border-cyan-500/20 text-cyan-300",
  purple: "bg-purple-500/10 border-purple-500/20 text-purple-300",
};

export default function Projects() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="projects" className="section-padding relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-950/10 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto relative">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-3">
            What I&apos;ve built
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            Featured{" "}
            <span className="gradient-text">Projects</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, index) => (
            <motion.div
              key={project.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.1 + index * 0.12 }}
              whileHover={{ y: -6 }}
              className={`glass-card rounded-2xl overflow-hidden transition-all duration-300 ${project.borderHover} flex flex-col group`}
            >
              {/* Card gradient header */}
              <div className={`h-1.5 bg-gradient-to-r ${project.gradient} w-full`} />

              <div className="p-6 flex flex-col flex-1">
                {/* Title */}
                <h3 className="text-white font-bold text-base leading-snug mb-3 group-hover:text-blue-300 transition-colors">
                  {project.title}
                </h3>

                {/* Description */}
                <p className="text-slate-400 text-sm leading-relaxed mb-4 flex-1">
                  {project.description}
                </p>

                {/* Tech badges */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {project.tech.map((t) => (
                    <span
                      key={t}
                      className={`px-2 py-0.5 rounded-md text-xs font-medium border ${
                        techColorMap[t] || defaultTechColor
                      }`}
                    >
                      {t}
                    </span>
                  ))}
                </div>

                {/* Impact */}
                <div
                  className={`flex items-start gap-2 p-3 rounded-xl border text-xs leading-relaxed mb-5 ${
                    impactColorMap[project.impactColor]
                  }`}
                >
                  <Zap size={12} className="mt-0.5 flex-shrink-0" />
                  <span>{project.impact}</span>
                </div>

                {/* Action buttons */}
                <div className="flex items-center gap-2">
                  <a
                    href="#"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium glass-card hover:bg-white/10 text-slate-300 hover:text-white transition-all"
                  >
                    <Github size={13} />
                    GitHub
                  </a>
                  <a
                    href="#"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium glass-card hover:bg-white/10 text-slate-300 hover:text-white transition-all"
                  >
                    <ExternalLink size={13} />
                    Live Demo
                  </a>
                  <a
                    href="#"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium glass-card hover:bg-white/10 text-slate-300 hover:text-white transition-all"
                  >
                    <BookOpen size={13} />
                    Case Study
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
