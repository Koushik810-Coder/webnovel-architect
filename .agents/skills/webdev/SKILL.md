---
name: webdev
description: Guidelines and best practices for building modern web applications, focusing on React, Vite, and high-quality UX design.
---

# Web Development Skill (React & Vite)

Follow this systematic approach when building frontend web applications:

## 1. Setup & Tooling
- Use **Vite** for React scaffolding (`npx create-vite`).
- Use **React Router** for declarative client-side routing.
- Keep dependencies minimal to ensure fast load times.

## 2. Design Aesthetics
- The user is extremely sensitive to UI aesthetics. The design must be modern, polished, and dynamic.
- **Do not use Tailwind CSS** unless explicitly requested. Use modular or global vanilla CSS (`index.css`) utilizing CSS variables for themeing.
- **Glassmorphism**: Use translucent backgrounds (`rgba(...)`) with `backdrop-filter: blur(12px)`.
- **Typography**: Apply modern web fonts (e.g., Inter, Roboto).
- **Animations**: Include micro-interactions (e.g., hover states mapping to `transform: translateY(-5px)` and box-shadows).

## 3. Architecture & Components
- Break the UI down into logically separate components (`components/Library.jsx`, `components/Player.jsx`).
- Implement proper loading and error states for any asynchronous fetch calls to the API.

## 4. End-User Focus
- Avoid technical jargon in the UI. If the system is performing a complex RAG or ingestion task, mask it behind an intuitive loader ("Preparing your audiobook..." instead of "Awaiting LLM Semantic Extraction...").
- Maximize the usability of core features like media players, ensuring they are sticky or easily accessible regardless of scroll position.
