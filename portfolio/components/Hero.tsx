"use client";

import { motion } from "framer-motion";
import { MapPin, Mail, Phone, Github, Linkedin, ArrowDown } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.6, ease: "easeOut" },
  }),
};

export default function Hero() {
  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden px-4 sm:px-6 lg:px-8"
    >
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="blob absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600" />
        <div className="blob blob-delay-2 absolute top-1/2 right-1/4 w-80 h-80 bg-purple-600" />
        <div className="blob blob-delay-4 absolute bottom-1/4 left-1/2 w-72 h-72 bg-cyan-600" />
      </div>

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          custom={0}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8"
        >
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Open to new opportunities · Baltimore, MD
        </motion.div>

        {/* Headline */}
        <motion.h1
          custom={1}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6"
        >
          Hi, I&apos;m{" "}
          <span className="gradient-text">Jaswanth Ram</span>
          {" "}—{" "}
          <br className="hidden sm:block" />
          Data Analyst turning complex data into dashboards, insights, and
          business decisions.
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          custom={2}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="text-slate-400 text-lg sm:text-xl max-w-3xl mx-auto mb-10 leading-relaxed"
        >
          Data Analyst with 3+ years of experience building SQL pipelines,
          Python workflows, Power BI and Tableau dashboards, and automated
          reporting systems that improve operational visibility and
          decision-making.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          custom={3}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="flex flex-wrap items-center justify-center gap-4 mb-10"
        >
          <button
            onClick={() => scrollToSection("projects")}
            className="px-6 py-3 rounded-xl text-white font-semibold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 transition-all duration-200 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5"
          >
            View Projects
          </button>
          <a
            href="/Jaswanth_Ram_Resume.pdf"
            download
            className="px-6 py-3 rounded-xl font-semibold border border-white/20 text-white hover:bg-white/5 hover:border-white/30 transition-all duration-200 hover:-translate-y-0.5"
          >
            Download Resume
          </a>
          <button
            onClick={() => scrollToSection("contact")}
            className="px-6 py-3 rounded-xl font-semibold text-slate-300 hover:text-white hover:bg-white/5 transition-all duration-200 hover:-translate-y-0.5"
          >
            Contact Me
          </button>
        </motion.div>

        {/* Info chips */}
        <motion.div
          custom={4}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="flex flex-wrap items-center justify-center gap-4 text-sm text-slate-400 mb-8"
        >
          <span className="flex items-center gap-1.5">
            <MapPin size={14} className="text-blue-400" />
            Baltimore, MD
          </span>
          <span className="text-slate-700">·</span>
          <a
            href="mailto:jrnagabhy@gmail.com"
            className="flex items-center gap-1.5 hover:text-blue-400 transition-colors"
          >
            <Mail size={14} className="text-blue-400" />
            jrnagabhy@gmail.com
          </a>
          <span className="text-slate-700">·</span>
          <a
            href="tel:+14435404434"
            className="flex items-center gap-1.5 hover:text-blue-400 transition-colors"
          >
            <Phone size={14} className="text-blue-400" />
            +1 (443) 540-4434
          </a>
        </motion.div>

        {/* Social Icons */}
        <motion.div
          custom={5}
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          className="flex items-center justify-center gap-4"
        >
          <a
            href="#"
            className="p-3 rounded-xl glass-card text-slate-400 hover:text-blue-400 hover:border-blue-500/30 transition-all duration-200 hover:-translate-y-0.5"
            aria-label="LinkedIn"
          >
            <Linkedin size={20} />
          </a>
          <a
            href="#"
            className="p-3 rounded-xl glass-card text-slate-400 hover:text-blue-400 hover:border-blue-500/30 transition-all duration-200 hover:-translate-y-0.5"
            aria-label="GitHub"
          >
            <Github size={20} />
          </a>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.6 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-600"
        >
          <span className="text-xs tracking-widest uppercase">Scroll</span>
          <ArrowDown size={14} className="animate-bounce" />
        </motion.div>
      </div>
    </section>
  );
}
