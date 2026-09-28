---
name: scaffold-clean-architecture
description: Scaffolds brand-new projects using Clean Architecture so business rules stay isolated from infrastructure, frameworks, and transport. Use when starting a project from scratch or when the user explicitly asks for clean, hexagonal, or ports-and-adapters structure for a new project. Do not use for changes to an existing codebase, including adding new services, modules, or components to an existing repository — those must follow the repository's current architecture.
---

# Scaffold Clean Architecture

Bootstrap a new project where **business rules are independent of infrastructure**.
The goal is not folder purity. The goal is that swapping a database, framework, or
transport never requires touching domain logic.

## Scope check (do this first)

Use this skill only when:
- The project does not exist yet — a new repository or a genuinely standalone new project, or
- The user explicitly asks for clean/hexagonal/ports-and-adapters structure for a new project.

Do **not** use it when:
- Modifying an existing codebase.
- Adding a service, module, or component to an existing repository — new parts of an
  existing system follow that system's current architecture and conventions.
- The code is a throwaway script, spike, or one-off.
- The component has a single trivial responsibility and no business rules.

If unsure, ask exactly one question: *"Is this a brand-new project, or a change to an existing repository?"*

## Non-negotiables

1. **Dependency rule** — source dependencies point inward, toward the domain. Nothing inner knows about anything outer.
2. **Domain purity** — domain code imports no framework, no DB driver, no HTTP client, no ORM, no serialization library. Plain language constructs only.
3. **Ports belong to the inside** — an interface is declared by the layer that *consumes* it, not the layer that implements it.
4. **Testable without infrastructure** — domain and use cases must be testable with zero I/O, no containers, no network.
5. **Pragmatism over ceremony** — 3-4 layers is almost always enough. Every abstraction must earn its place.

## Workflow

### 1. Gather constraints (briefly)

Determine, inferring when obvious:
- Language + runtime
- Framework (web, CLI, worker) — or none
- Persistence (relational, document, none)
- Inbound transport (HTTP, queue, cron, CLI)
- Outbound integrations (APIs, queues, object storage)

Ask only for what you cannot infer. Do not interrogate the user.

### 2. Choose the layer count

Default to four layers, ordered from the innermost (most stable) to the
outermost:

```
domain | application | infrastructure | entrypoints
```

Collapse to three when there is no meaningful inbound transport layer:

```
domain | application | infrastructure
```

Do not exceed four. Do not invent intermediate layers. In this skill `→` always
means "depends on"; direction is defined in the "Dependency rules" section.

### 3. Scaffold the structure

The tree below describes layer responsibilities, not fixed directory names. The root
and names follow the language and ecosystem convention: `src/` for TypeScript/Node,
`internal/` for Go (see `go-expert`), `src/main/java` for Java, and so on. When a
language-convention skill defines a layout, its layout wins.

```
<root>/
  domain/
    entities/          # business objects with behavior
    value-objects/     # immutable, validated primitives
    services/          # domain logic that spans entities
    errors/            # domain-specific error types
  application/
    use-cases/         # one class/function per business action
    ports/             # interfaces the application consumes
    dto/               # input/output shapes at the app boundary
  infrastructure/
    persistence/       # implements repository ports
    gateways/          # implements external-service ports
    config/            # env parsing, config objects
  entrypoints/
    http/              # or cli/, queue/, cron/
      routes/
      controllers/
tests/
  domain/
  application/
  infrastructure/
```

### 4. Build one vertical slice

Do not leave empty folders. Implement **one complete, trivial feature end-to-end**
so every layer has a working exemplar. Pick something minimal but real — "create a
widget", "fetch an exchange rate".

The slice must exercise every layer:

- the entrypoint calls a use case
- the use case depends on a port, declared where it is consumed
- an adapter in `infrastructure` implements that port
- domain types and rules sit at the center, used by the use case and the adapter

In arrow notation (`→` means depends on, `←` means implements):
`entrypoint → use case → port ← adapter`, with both the use case and the adapter
depending on `domain`.

...with tests covering the domain, application, and infrastructure code it touches.

This slice is the template every future feature copies. It matters more than the
folder names. Empty scaffolding teaches nothing; a working slice teaches everything.

### 5. Add enforcement

Architecture that is only documented will drift. Add at least one **executable**
constraint that fails the build on a backward dependency.

| Stack | Option |
|---|---|
| TypeScript / Node | `dependency-cruiser`, `eslint-plugin-boundaries` |
| Java / Kotlin | ArchUnit |
| Python | `import-linter` |
| Go | `go-arch-lint`, `depguard` (via golangci-lint) |
| .NET | NetArchTest |
| Rust | integration test asserting the module graph |
| Anything | a plain test that scans import statements |

If no tool fits, write the plain import-scanning test. A rule without a failing
build is a suggestion.

### 6. Seed tests

- **Domain** — pure unit tests for business rules. No mocks required.
- **Application** — use case tests with hand-written fake ports. No framework boot.
- **Infrastructure** — adapter tests against the real dependency (test container) or a contract test.

Entrypoints are not a test layer. Keep them thin and cover their behavior through the
use cases they call. When a test needs to drive an entrypoint, add a test-specific
entrypoint (a fake HTTP server, a test CLI) rather than growing tests around the
production one.

If domain tests need a mocking framework, the boundary is wrong.

### 7. Document for agents and humans

Write an `AGENTS.md` (or `CLAUDE.md`) containing:
- The layer list and what belongs in each
- The dependency rule, stated explicitly
- Where ports live vs. where adapters live
- The exact command that verifies architecture
- A pointer to the exemplar vertical slice

Keep it short and imperative. This file is the contract future agents read first.
(If you have an `AGENTS.md` generator skill, this closes the loop — scaffold, then
let it document.)

### 8. Verify and report

Run the build, the tests, and the architecture check. Report:
- Chosen layers and why
- The exemplar slice
- The enforcement command
- What was intentionally left out

## Dependency rules

**Allowed**
- `entrypoints → application, infrastructure, domain`
- `infrastructure → application` (implements ports), `→ domain`
- `application → domain`
- `domain → nothing`

Entrypoints may reference domain types — for example, to map a domain error to a
transport response — but business rules stay in the domain and use cases.

**Forbidden**
- `domain →` anything outer or any framework
- `application →` infrastructure, entrypoints, or any framework/ORM/HTTP type
- `infrastructure →` entrypoints
- Anything reaching into another feature's internals

The composition root — where adapters are wired to ports — lives in `entrypoints`.
That is the one place outer layers are allowed to know each other. In the
three-layer variant there is no `entrypoints` layer: the composition root lives in
the outermost module, or in the embedding application when the project is consumed
as a library.

## Ports and adapters

Ports (interfaces) live inside the boundary they serve, declared by the layer that
consumes them — never by the layer that implements them. Default to
`application/ports/` for ports consumed by use cases; put the port in `domain/` when
domain logic consumes it directly (for example a repository contract used by a domain
service). Adapters (implementations) live in `infrastructure`.

When a language-convention skill defines the layout for a stack, follow it. For Go,
`go-expert` places repository and client contracts under `domain/` and their
implementations under `infrastructure/`.

A port is named in **domain terms**, never vendor terms:

| Good | Bad |
|---|---|
| `UserRepository` | `PostgresUserDao` |
| `PaymentGateway` | `StripeClient` |
| `Clock` | `SystemTimeProvider` |

Mapping between domain objects and persistence rows belongs in `infrastructure`,
never in the domain.

## Anti-patterns

- **Anemic domain + fat services.** If the domain is only data holders, business rules leaked into use cases.
- **A port per table.** A repository models intent, not schema. Not every table needs its own interface.
- **Layers for their own sake.** A mapper between two identical shapes is noise.
- **Framework-annotated entities.** ORM, validation, or serialization decorators on domain classes break purity.
- **`utils/` as a back door.** Shared helpers must not become a channel between layers.
- **Empty scaffolding.** Folders without code are documentation, not structure.
- **Skipping enforcement.** See above.
- **Over-engineering a small thing.** If the domain is genuinely trivial, a three-layer structure with one port may be the honest answer.

## Done criteria

- [ ] One vertical slice works end-to-end
- [ ] Domain imports no framework or I/O library
- [ ] Ports declared where they are consumed, implemented in `infrastructure`
- [ ] Domain and use case tests run with no infrastructure
- [ ] An automated check fails on a backward dependency
- [ ] `AGENTS.md` documents layers, the dependency rule, and the check command
- [ ] Build, tests, and architecture check all pass
