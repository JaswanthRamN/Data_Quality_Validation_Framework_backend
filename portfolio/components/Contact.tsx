"use client";

import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef, useState } from "react";
import { Mail, Phone, MapPin, Send, Github, Linkedin, CheckCircle } from "lucide-react";

export default function Contact() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", message: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <section id="contact" className="section-padding relative">
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
            Let&apos;s connect
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">
            Get in{" "}
            <span className="gradient-text">Touch</span>
          </h2>
          <div className="mt-4 h-1 w-20 mx-auto rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-10">
          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass-card rounded-2xl p-6 sm:p-8"
          >
            {submitted ? (
              <div className="flex flex-col items-center justify-center h-full py-12 text-center">
                <CheckCircle size={48} className="text-green-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Message sent!</h3>
                <p className="text-slate-400">
                  Thanks for reaching out. I&apos;ll get back to you soon.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <h3 className="text-xl font-bold text-white mb-1">Send a message</h3>
                <p className="text-slate-400 text-sm mb-6">
                  Have a project in mind or want to discuss an opportunity? I&apos;d love to hear from you.
                </p>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="Your name"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/8 transition-all text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/8 transition-all text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Message
                  </label>
                  <textarea
                    required
                    rows={5}
                    value={form.message}
                    onChange={(e) => setForm({ ...form, message: e.target.value })}
                    placeholder="Tell me about your project or opportunity..."
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/8 transition-all text-sm resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-white font-semibold bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 transition-all duration-200 shadow-lg shadow-blue-500/20 hover:-translate-y-0.5"
                >
                  <Send size={16} />
                  Send Message
                </button>
              </form>
            )}
          </motion.div>

          {/* Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="space-y-4"
          >
            {[
              {
                icon: Mail,
                label: "Email",
                value: "jrnagabhy@gmail.com",
                href: "mailto:jrnagabhy@gmail.com",
              },
              {
                icon: Phone,
                label: "Phone",
                value: "+1 (443) 540-4434",
                href: "tel:+14435404434",
              },
              {
                icon: MapPin,
                label: "Location",
                value: "Baltimore, MD",
                href: null,
              },
              {
                icon: CheckCircle,
                label: "Open to Relocation",
                value: "Yes",
                href: null,
              },
            ].map((item) => (
              <div
                key={item.label}
                className="glass-card rounded-2xl p-5 hover:bg-white/6 transition-all duration-300 group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20">
                    <item.icon size={18} className="text-blue-400" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-0.5">
                      {item.label}
                    </div>
                    {item.href ? (
                      <a
                        href={item.href}
                        className="text-slate-200 font-medium hover:text-blue-400 transition-colors text-sm"
                      >
                        {item.value}
                      </a>
                    ) : (
                      <span className="text-slate-200 font-medium text-sm">
                        {item.value}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Social links */}
            <div className="glass-card rounded-2xl p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-4">
                Connect on
              </p>
              <div className="flex gap-3">
                <a
                  href="#"
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl glass-card hover:bg-white/10 text-slate-300 hover:text-blue-400 transition-all text-sm font-medium"
                >
                  <Linkedin size={16} />
                  LinkedIn
                </a>
                <a
                  href="#"
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl glass-card hover:bg-white/10 text-slate-300 hover:text-blue-400 transition-all text-sm font-medium"
                >
                  <Github size={16} />
                  GitHub
                </a>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
