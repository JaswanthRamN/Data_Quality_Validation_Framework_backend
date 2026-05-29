# Jaswanth Ram Nagabhyrava — Portfolio

Modern personal portfolio website built with Next.js 14, TypeScript, Tailwind CSS, and Framer Motion.

## Quick Start

```bash
cd portfolio
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
portfolio/
├── app/
│   ├── layout.tsx        # SEO metadata, fonts, root layout
│   ├── page.tsx          # Main page — imports all sections
│   └── globals.css       # Global styles, Tailwind directives
├── components/
│   ├── Navbar.tsx        # Sticky nav with active section tracking
│   ├── Hero.tsx          # Hero with animated blobs and CTAs
│   ├── About.tsx         # About + stats cards
│   ├── Skills.tsx        # 6 skill category cards
│   ├── Experience.tsx    # Vertical timeline
│   ├── Projects.tsx      # 3 project cards with tech badges
│   ├── Education.tsx     # 2 education cards
│   ├── Resume.tsx        # Resume download CTA
│   ├── Contact.tsx       # Contact form + info cards
│   └── Footer.tsx        # Footer with social links
└── public/
    └── Jaswanth_Ram_Resume.pdf   ← PLACE YOUR RESUME PDF HERE
```

## Adding Your Resume PDF

1. Export your resume as a PDF
2. Name it exactly: `Jaswanth_Ram_Resume.pdf`
3. Place it in the `public/` folder: `portfolio/public/Jaswanth_Ram_Resume.pdf`
4. The download button in the Resume and Hero sections will work automatically

## Updating Links

Search for `href="#"` in the component files and replace with real URLs:

| Component | What to update |
|-----------|----------------|
| `Hero.tsx` | LinkedIn and GitHub icon hrefs |
| `Projects.tsx` | GitHub repo, Live Demo, and Case Study links for each project |
| `Contact.tsx` | LinkedIn and GitHub hrefs |
| `Footer.tsx` | LinkedIn and GitHub hrefs |

Example — LinkedIn:
```tsx
// Before
<a href="#">

// After  
<a href="https://linkedin.com/in/your-profile">
```

## Deploy to Vercel

1. Push the `portfolio/` folder to GitHub (already done on branch `claude/jaswanth-portfolio-site-kkvEQ`)
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo
3. Set **Root Directory** to `portfolio`
4. Click **Deploy** — Vercel auto-detects Next.js

## Tech Stack

- **Next.js 14** (App Router, static export)
- **TypeScript** — full type safety
- **Tailwind CSS** — utility-first styling
- **Framer Motion** — scroll-triggered animations
- **Lucide React** — icons

## Customization

- Colors: edit `tailwind.config.ts` and `globals.css`
- Content: each component file contains its own data — no separate data files
- Fonts: swap `Inter` in `app/layout.tsx` for any Google Font
