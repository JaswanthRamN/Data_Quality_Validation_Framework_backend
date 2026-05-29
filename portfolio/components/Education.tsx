"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { GraduationCap, MapPin } from "lucide-react";

const education = [
  {
    degree: "Master of Science in Information Systems",
    school: "University of Maryland, Baltimore County",
    location: "Baltimore, MD",
    gradient: "from-blue-600/20 to-cyan-600/20",
    border: "hover:border-blue-500/30",
    badgeColor: "bg-blue-500/10 border-blue-500/20 text-blue-300",
  },
  {
    degree: "Bachelor of Technology in Automobile Engineering",
    school: "Hindustan Institute of Technology and Science",
    location: "Chennai, India",
    gradient: "from-purple-600/20 to-pink-600/20",
    border: "hover:border-purple-500/30",
    badgeColor: "bg-purple-500/10 border-purple-500/20 text-purple-300",
  },
];

export default function Education() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="education" className="section-padding relative">
      <div className="max-w-4xl mx-auto">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-3">
            Academic background
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            <span className="gradient-text">Education</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-6">
          {education.map((edu, index) => (
            <motion.div
              key={edu.school}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.2 + index * 0.15 }}
              className={`glass-card rounded-2xl overflow-hidden transition-all duration-300 ${edu.border} group`}
            >
              <div className={`h-1.5 bg-gradient-to-r ${edu.gradient}`} />
              <div className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-white/5 flex-shrink-0">
                    <GraduationCap size={22} className="text-blue-400 group-hover:scale-110 transition-transform" />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-base leading-snug mb-2">
                      {edu.degree}
                    </h3>
                    <p className="text-slate-300 font-medium text-sm mb-2">
                      {edu.school}
                    </p>
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${edu.badgeColor}`}
                    >
                      <MapPin size={11} />
                      {edu.location}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
