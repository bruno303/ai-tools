---
name: nextjs-frontend-guidelines
description: Next.js-specific frontend architecture, App Router conventions, and delivery standards.
---

## 1. Project Detection
- Apply this skill only when the project clearly uses Next.js (for example: `next` in `package.json`, `next.config.*`, or a standard `app/` or `pages/` directory).

## 2. Routing and File Placement
- Follow the routing system already in use. Do not mix `app/` and `pages/` conventions unless the repository already does so intentionally.
- In App Router projects, keep route composition in `page.tsx`, shared shells in `layout.tsx`, request lifecycle logic in route handlers, and reusable UI in colocated or shared components.
- Place reusable primitives in the project's existing shared UI location (`components/`, `src/components/`, feature folders, etc.) instead of duplicating markup in route files.

## 3. Server and Client Boundaries
- Default to Server Components. Add `"use client"` only when interactivity, browser APIs, local state, refs, or client-only hooks are required.
- Keep client components as small leaf nodes whenever possible. Pass serialized data down from server components rather than moving whole trees to the client.
- Do not import server-only modules into client components.

## 4. Data Fetching and Mutations
- Prefer server-side data fetching in App Router pages, layouts, and server components.
- Use Server Actions or route handlers only when they match the existing project patterns for mutations.
- Keep fetch logic close to the route or feature that owns it, but extract shared API/domain logic when it is reused across multiple surfaces.
- Handle loading, empty, and error states explicitly.

## 5. State Management
- Prefer local state first. Introduce shared client state only when multiple distant components truly need coordinated state.
- Derive UI state from props, URL params, and server data before adding client stores or effects.
- Avoid redundant fetch-on-mount patterns when data is already available from the server.

## 6. UX and Frontend Quality
- Preserve the existing visual language, component patterns, tokens, and styling approach already used by the repository.
- New UI must be responsive across mobile and desktop layouts.
- Build accessible interfaces: semantic HTML, keyboard support, visible focus states, correct labels, and sensible ARIA only when native elements are insufficient.
- Optimize for perceived performance: avoid oversized client bundles, unnecessary re-renders, and avoidable hydration.

## 7. Next.js Conventions
- Use `next/link`, `next/image`, metadata APIs, and other framework primitives when appropriate and already supported by the codebase.
- Respect caching and rendering choices already present in the project. If changing static/dynamic behavior, do so intentionally and only where needed.
- Use environment variables and runtime boundaries consistent with Next.js and the existing deployment model. Never leak server secrets to the client.

## 8. Verification
- Run the repository's frontend verification commands after implementation. Prefer the existing package manager and scripts such as `npm run lint`, `npm run build`, `pnpm lint`, or equivalent.
