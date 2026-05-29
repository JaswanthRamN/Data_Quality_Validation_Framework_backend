"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef } from "react";
import { Download, FileText } from "lucide-react";

export default function Resume() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="resume" className="section-padding relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-950/30 via-purple-950/20 to-transparent pointer-events-none" />
      <div className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: "radial-gradient(circle at 50% 50%, #3b82f6 0%, transparent 70%)",
        }}
      />

      <div className="max-w-3xl mx-auto relative text-center">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl glass-card mb-6">
            <FileText size={28} className="text-blue-400" />
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Want the full{" "}
            <span className="gradient-text">resume?</span>
          </h2>

          <p className="text-slate-400 text-lg leading-relaxed mb-8 max-w-xl mx-auto">
            Download my resume to see my complete experience, technical skills,
            and project background.
          </p>

          {/* Place resume PDF at: public/Jaswanth_Ram_Resume.pdf */}
          <a
            href="/Jaswanth_Ram_Resume.pdf"
            download
            className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl text-white font-semibold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 transition-all duration-200 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5 text-base"
          >
            <Download size={20} />
            Download Resume
          </a>

          <p className="mt-4 text-slate-600 text-sm">
            PDF · Updated 2025
          </p>
        </motion.div>
      </div>
    </section>
  );
}
