"use client";

import { Github, Linkedin, Mail } from "lucide-react";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-white/8 py-10 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        {/* Brand */}
        <div className="text-center sm:text-left">
          <p className="text-slate-300 font-medium">
            Built by{" "}
            <span className="gradient-text font-semibold">
              Jaswanth Ram Nagabhyrava
            </span>
          </p>
          <p className="text-slate-600 text-sm mt-1">
            © {year} · Data Analyst · Baltimore, MD
          </p>
        </div>

        {/* Social Links */}
        <div className="flex items-center gap-3">
          <a
            href="#"
            className="p-2.5 rounded-xl glass-card text-slate-400 hover:text-blue-400 hover:border-blue-500/30 transition-all duration-200"
            aria-label="LinkedIn"
          >
            <Linkedin size={18} />
          </a>
          <a
            href="#"
            className="p-2.5 rounded-xl glass-card text-slate-400 hover:text-blue-400 hover:border-blue-500/30 transition-all duration-200"
            aria-label="GitHub"
          >
            <Github size={18} />
          </a>
          <a
            href="mailto:jrnagabhy@gmail.com"
            className="p-2.5 rounded-xl glass-card text-slate-400 hover:text-blue-400 hover:border-blue-500/30 transition-all duration-200"
            aria-label="Email"
          >
            <Mail size={18} />
          </a>
        </div>
      </div>
    </footer>
  );
}
