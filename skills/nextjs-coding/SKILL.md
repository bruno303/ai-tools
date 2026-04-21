---
name: nextjs-coding
description: Use when writing or reviewing Next.js frontend code to ensure it follows common conventions for readability, maintainability, and correctness.
---

# When to use

Use these defaults when reading, generating, or reviewing Next.js frontend code.

# Project fit
- Apply these rules only when the project clearly uses Next.js.
- Detect whether the feature belongs to App Router or Pages Router.
- Do not mix `app/` and `pages/` patterns casually inside the same feature.
- Before adding code, inspect a few similar routes/components/tests and follow the local convention.

# Routing and file placement
- Keep route entry files thin.
- In App Router:
  - `page.*` should compose route UI
  - `layout.*` should own shared route shells
  - `loading.*` should provide loading UI
  - `error.*` should handle recoverable route errors
  - `route.*` should be used for HTTP behavior, not page UI
- In Pages Router, page files should delegate reusable UI and logic to nearby modules or shared components.
- Put shared UI in the project’s existing shared location.
- Keep feature-specific helpers close to the feature unless reused elsewhere.

# Server and client boundaries
- In App Router, default to Server Components.
- Add `"use client"` only when needed for:
  - event handlers
  - browser APIs
  - refs
  - local interactive state
  - client-only hooks
  - client-side context consumption
- Keep client components as small leaf components when possible.
- Do not import server-only code, secrets, or Node-only utilities into client components.
- Only pass serializable data from server components to client components.

# Data fetching and rendering
- Prefer server-side data fetching when data is available at render/request time.
- In Pages Router, follow the project’s existing data-fetching pattern.
- Keep fetching logic close to the owning feature.
- Extract shared API/domain logic only once it is reused.
- Handle user-visible loading, empty, error, and success states explicitly.
- Do not change caching, rendering mode, or revalidation behavior accidentally.
- When cache invalidation or revalidation is needed, make the trigger explicit.

# Mutations and forms
- Follow the repository’s existing mutation pattern.
- In App Router, prefer Server Actions for form-oriented mutations only when the project already uses them and they fit naturally.
- Use route handlers or API routes when the behavior is HTTP-oriented or used by multiple clients.
- Forms should expose meaningful pending, success, and error states.
- Add optimistic UI only when the UX benefit is clear and the project can support the extra complexity.

# State and URL
- Prefer local component state first.
- Introduce shared client state only when multiple distant client components truly need it.
- Derive UI state from props, server data, route params, and search params before adding effects or client stores.
- Put shareable or navigable state in the URL when that matches the product behavior.
- Avoid fetch-on-mount when the same data could come from the server render path.

# Framework usage
- Use Next.js primitives already accepted by the project, such as:
  - `next/link`
  - `next/image`
  - metadata APIs
  - dynamic imports
- Keep metadata close to the route that owns it.
- Preserve the existing styling system, design tokens, and component conventions.

# UX, accessibility, and performance
- Build responsive UI by default.
- Accessibility is required:
  - semantic HTML
  - keyboard support
  - visible focus states
  - correct labels
  - ARIA only when native elements are insufficient
- Optimize for perceived performance:
  - minimize unnecessary hydration
  - keep client bundles small
  - avoid unnecessary re-renders
  - avoid turning large trees into client components

# Testing
- Test meaningful application behavior, not Next.js internals.
- For server components, test rendered outcomes and route-level states.
- For client components, test user interaction and observable state changes.
- For route handlers or API routes, test validation, response shape, status codes, and meaningful error paths.
- Cover loading, empty, error, and success states when they are part of the UX.
- Do not add tests for trivial wrappers or framework behavior that Next.js already guarantees.

# Verification
- Run the project’s existing lint, test, type-check, and build commands.
- Start with the narrowest relevant command, then broader validation when needed.
- Use the package manager and scripts already adopted by the repository.
