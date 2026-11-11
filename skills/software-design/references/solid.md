# SOLID as a Diagnostic

SOLID is a set of heuristics for finding expensive coupling and change
fragility. A principle violation is only a finding when it produces a concrete
cost: harder change, duplicated rules, fragile substitution, unnecessary
coupling, or tests that need unrelated infrastructure.

Use SOLID to explain the cost, not to justify a rewrite. A small cohesive module
with a textbook violation can be better than a fragmented design that satisfies
every letter.

## Single Responsibility Principle (SRP)

- **Intent.** A module should have one reason to change: one actor or
  stakeholder whose needs drive it.
- **Smells.** Unrelated actors share a class; methods change for different
  reasons; a name needs "and", "Manager", or "Helper"; tests need large setup
  for unrelated behavior; changes for one feature break another.
- **Safe response.** Split by reason to change, extract a cohesive collaborator,
  or move behavior next to the data and rules it owns. Name the responsibility
  after the split.
- **When not to apply.** The module is small, cohesive, and driven by one actor;
  splitting would force navigation across many files for one concept; the split
  is merely technical with no independent reason to change.
- **Counterweight.** SRP is about reasons to change, not "one function per file".
  Excessive splitting scatters a single concept and raises the cost of
  understanding it.

## Open/Closed Principle (OCP)

- **Intent.** Add behavior without modifying stable existing code.
- **Smells.** A growing `switch` or `if` chain on type or status; every new
  variant edits the same central conditional; feature flags spread across
  unrelated modules.
- **Safe response.** Introduce a polymorphism seam only on the axis that
  genuinely varies, such as a strategy or hook. Keep the default path open and
  test each variant through the same contract.
- **When not to apply.** There is one stable case, the second variant is
  speculative, or the extension point has no real implementation yet. An
  abstraction with one implementation is usually just indirection.
- **Counterweight.** YAGNI. The first variation is often just data; wait for a
  real second variant. OCP must not freeze code that should change.

## Liskov Substitution Principle (LSP)

- **Intent.** A subtype must honor the contract of the type it replaces.
- **Smells.** Overrides throw "not implemented"; preconditions are strengthened
  or postconditions weakened; callers check the concrete type before use; base
  methods are overridden to do nothing.
- **Safe response.** Fix or narrow the contract, model the difference with
  composition, split the interface, or make invalid states unrepresentable. Test
  that the substitute preserves observable behavior.
- **When not to apply.** There is no subtype relationship, or the shared type is
  only a narrow consumer interface with no behavioral promise beyond its methods.
- **Counterweight.** Rich contracts are harder to implement. Do not force a
  common base type when the behaviors genuinely differ; LSP is about behavioral
  substitutability, not matching method signatures.

## Interface Segregation Principle (ISP)

- **Intent.** Clients should not depend on methods they do not use.
- **Smells.** Fat interfaces; implementers with empty methods; mocks with many
  unused methods; test setup dominated by irrelevant capabilities.
- **Safe response.** Split interfaces by consumer need, define them at the
  consumer boundary, and accept multiple narrow contracts when a collaborator
  fulfills them.
- **When not to apply.** One cohesive interface with one real consumer is
  already small enough. Splitting a capability into single-method interfaces
  multiplies types without reducing coupling.
- **Counterweight.** Interface proliferation. Too many tiny interfaces obscure
  the model; group by cohesive capability, not by individual method.

## Dependency Inversion Principle (DIP)

- **Intent.** High-level policy should not depend on low-level detail; both
  should depend on abstractions.
- **Smells.** Domain code imports framework, database, or transport packages;
  business logic constructs infrastructure directly; static or global clients;
  tests need a real external system.
- **Safe response.** Define a port at the consumer boundary, inject the
  implementation, keep dependency direction inward, and wire concrete types at
  the composition root.
- **When not to apply.** A trivial script, a stable same-layer helper, or a
  dependency that is genuinely an implementation detail. An interface with one
  implementation and no substitution need may cost more than it saves.
- **Counterweight.** Unnecessary indirection. Dependency injection is a wiring
  principle, not a framework requirement; the goal is explicit dependencies, not
  a container or a diagram.

## Using SOLID without over-abstracting

- Name the concrete change the design makes easier before applying a principle.
- Prefer the smallest seam that isolates the varying part.
- Wait for a real second implementation before generalizing.
- Keep interfaces at consumer boundaries and only as large as the use requires.
- Prefer composition unless inheritance already models the domain.
- Treat every additional type, layer, and injection point as a cost to justify.
- If two designs solve the force equally, choose the one with fewer concepts and
  easier debugging.
