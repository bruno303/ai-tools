---
name: nextjs-frontend-guidelines
description: Next.js-specific frontend architecture, App Router conventions, and delivery standards.
---

## 1. Project Detection
- Apply this skill only when the repository clearly uses Next.js, for example: `next` in `package.json`, `next.config.*`, `app/`, or `pages/`.
- If the repository contains both `app/` and `pages/`, agents MUST identify which routing system owns the feature being changed and follow that local convention.

## 2. Onboarding Protocol (Agent Task)
- Before writing code or tests, the agent MUST inspect the current routing system, styling approach, data-fetching pattern, and test setup used by the project.
- The agent MUST read 2-3 similar routes, components, or tests before deciding where new code belongs.
- The agent MUST identify the project's Source of Truth for:
  - route file placement
  - server/client component boundaries
  - form handling and mutations
  - loading, empty, and error states
  - frontend test style and helpers
- If multiple valid patterns exist and the choice would materially affect the design, the agent MUST ask one targeted question. Otherwise, the agent MUST choose the most consistent option and proceed.

## 3. Routing and File Placement
- Agents MUST follow the routing system already in use. Do not mix `app/` and `pages/` conventions unless the repository already does so intentionally.
- In App Router projects:
  - `page.*` SHOULD compose route-level content
  - `layout.*` SHOULD own shared shells for a route subtree
  - `loading.*` SHOULD handle route-segment loading UI
  - `error.*` SHOULD handle recoverable route-segment failures
  - `route.*` MUST be reserved for HTTP handler behavior, not page UI
- In Pages Router projects, page entry files SHOULD stay thin and delegate reusable UI and data logic to nearby modules or shared components.
- Reusable primitives and shared UI MUST be placed in the project's existing shared location such as `components/`, `src/components/`, or feature folders rather than duplicated inside route files.
- Feature-specific helpers SHOULD stay close to the route or feature that owns them unless they are reused elsewhere.

## 4. Server and Client Boundary Rules
- In App Router projects, Server Components MUST be the default.
- `"use client"` MUST be added only when a component needs browser APIs, event handlers, refs, local interactive state, client-only hooks, or client-side context consumption.
- Client components SHOULD remain small leaf nodes whenever possible.
- Data fetching SHOULD stay on the server when the data is available at request or render time.
- Server components MAY pass serialized data to client components, but agents MUST NOT pass non-serializable values across the boundary.
- Agents MUST NOT import server-only modules, secret-bearing utilities, or Node-only code into client components.

## 5. Data Fetching, Rendering, and Caching
- In App Router projects, data fetching SHOULD happen in server components, layouts, or route handlers unless the interaction is inherently client-driven.
- In Pages Router projects, agents MUST follow the existing project pattern for `getServerSideProps`, `getStaticProps`, client fetching, or API-layer abstractions.
- Fetching logic SHOULD live close to the route or feature that owns it, but shared API or domain logic SHOULD be extracted once reused across multiple surfaces.
- Agents MUST handle loading, empty, error, and success states explicitly when those states are user-visible.
- Static, dynamic, and revalidated behavior MUST be changed intentionally. Agents MUST preserve the project's existing caching model unless the task requires a different rendering mode.
- When revalidation or cache invalidation is used, the trigger and scope SHOULD be explicit and tied to the owning mutation flow.

## 6. Mutations and Forms
- Agents MUST follow the repository's existing mutation model: Server Actions, route handlers, API routes, client-side mutation libraries, or form-post patterns.
- In App Router projects, Server Actions SHOULD be preferred for form-oriented mutations when the repository already uses them and they fit the feature cleanly.
- Route handlers or API routes SHOULD be used when the repository already exposes HTTP endpoints, when non-form clients need the mutation, or when the behavior is transport-oriented.
- Forms MUST provide meaningful pending, success, and error behavior when the user can observe those states.
- Optimistic UI SHOULD be introduced only when the project already uses it or when the UX value clearly justifies the added complexity.

## 7. State and URL Rules
- Agents SHOULD prefer local component state first.
- Shared client state SHOULD be introduced only when multiple distant client components truly need coordinated state.
- UI state SHOULD be derived from props, server data, route params, and search params before adding effects or client stores.
- Shareable or navigable state such as filters, sort order, tabs, pagination, or selected IDs SHOULD live in the URL when that matches the existing product behavior.
- Agents MUST avoid redundant fetch-on-mount patterns when equivalent data is already available from the server render path.

## 8. Framework Conventions and Delivery Quality
- Agents SHOULD use Next.js primitives already supported by the codebase, such as `next/link`, `next/image`, metadata APIs, font utilities, and dynamic imports.
- Metadata SHOULD be defined using the project's existing Next.js pattern and kept close to the route that owns it.
- New UI MUST preserve the existing design system, tokens, styling approach, and component patterns used by the repository.
- New UI MUST be responsive across mobile and desktop layouts.
- Accessibility is mandatory: semantic HTML, keyboard support, visible focus states, correct labels, and ARIA only when native elements are insufficient.
- Agents MUST optimize for perceived performance by limiting client bundle size, avoiding unnecessary hydration, and preventing avoidable re-renders.

## 9. Testing Guidance
- `@builder` MUST use these rules to preserve testable server/client boundaries.
- `@test-writer` MUST use these rules when deciding what Next.js behavior deserves coverage.
- Tests SHOULD focus on meaningful application behavior rather than framework internals.
- Server component tests SHOULD verify rendered outcomes, fallback states, and route-level behavior without re-testing Next.js itself.
- Client component tests SHOULD cover user interactions, local state transitions, accessibility behavior, and observable mutation states.
- Route handler or API tests SHOULD cover request validation, response shaping, status codes, and meaningful error paths when the repository treats those handlers as owned behavior.
- Loading, empty, error, and success states SHOULD be tested when they are part of the changed user experience.
- Agents SHOULD NOT add tests for trivial markup wrappers, framework primitives, or behavior already guaranteed by Next.js unless the repository explicitly treats those wrappers as important contracts.

## 10. Anti-Patterns to Avoid
- Agents MUST NOT add `"use client"` to large trees when a smaller interactive leaf component would work.
- Agents MUST NOT fetch on mount for data that could be obtained during server rendering.
- Agents MUST NOT place reusable business or API logic directly inside route files when the project already extracts that logic into shared modules.
- Agents MUST NOT leak server secrets, private environment variables, or server-only dependencies into client bundles.
- Agents MUST NOT mix `app/` and `pages/` patterns casually inside the same feature.
- Agents MUST NOT change rendering mode, cache behavior, or runtime boundaries accidentally as a side effect of unrelated work.

## 11. Verification
- Agents MUST run the repository's existing verification commands after implementation or test changes.
- Agents SHOULD run the narrowest relevant command first, then broader verification when appropriate.
- Verification SHOULD use the repository's existing package manager and scripts, for example `pnpm test`, `pnpm lint`, `pnpm build`, `npm run test`, `npm run lint`, or `npm run build`.
- If the repository has distinct commands for unit tests, component tests, linting, type-checking, or production build validation, agents SHOULD use the commands relevant to the files changed.
