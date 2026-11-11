# Pattern Catalog

Use this catalog after identifying a concrete force. Each entry follows the same
shape. The sketches are language-neutral; translate them into the repository's
idioms instead of copying their structure literally.

If no entry fits, use a direct implementation. The catalog is a tool for naming
solutions, not a menu that requires a choice.

| Pattern | Typical force |
| --- | --- |
| Strategy | Interchangeable algorithms selected at runtime or composition time |
| Decorator | Optional behavior wrapped around an object without changing its type |
| Repository | Domain-oriented access isolated from persistence mechanics |
| Singleton | One genuinely process-wide instance with a controlled lifecycle |
| Factory | Creation choice and construction details hidden from callers |
| Builder | Complex object assembled step by step with validation |
| Adapter | Third-party or legacy interface translated to the domain contract |
| Chain of Responsibility | A request passes through handlers until one handles it |
| State | Behavior and legal transitions tied to an explicit lifecycle |
| Observer / Events | One event delivered to multiple independent consumers |
| Middleware | Cross-cutting processing around a request handler |
| Value Object | Immutable concept defined by its values and invariants |
| Unit of Work | Multiple changes committed as one transaction |
| Dependency Injection | Dependencies supplied from outside instead of constructed internally |

## Strategy

- **Intent.** Encapsulate interchangeable algorithms behind a common contract.
- **Problem / force.** Behavior varies by configuration, input, or environment;
  conditional branches keep growing; variants need independent tests.
- **Use when.** There are real variants with the same contract, selected at
  runtime or composition time, and the caller should not know which one runs.
- **Avoid when.** There is one implementation, two stable branches, or the
  variation is data rather than behavior. A direct conditional is clearer.
- **Structure.** A context holds a strategy interface; concrete strategies
  implement it; selection happens at the composition or use site.
- **Tradeoffs.** One type per variant and extra indirection; selection logic must
  live somewhere; call flow is harder to trace.
- **Common misuse.** A strategy for every boolean, an interface per method, or
  runtime selection when constructor injection would do.
- **Related SOLID.** OCP, DIP, ISP.
- **Sketch.**

```text
interface PricingStrategy { price(order) }
StandardPricing implements PricingStrategy
DiscountPricing implements PricingStrategy
Checkout(strategy: PricingStrategy).total(order) -> strategy.price(order)
```

## Decorator

- **Intent.** Attach behavior around an object while preserving its contract.
- **Problem / force.** Optional or cross-cutting behavior such as logging,
  caching, retry, compression, or authorization must be combined in different
  ways without changing the wrapped type.
- **Use when.** Behavior wraps the same interface, combinations are open-ended,
  and the underlying object should not know about the wrapper.
- **Avoid when.** There is one fixed wrapper, the project already has a
  middleware pipeline, or the wrapper changes the core contract rather than
  extending it.
- **Structure.** A component interface; a concrete component; a decorator that
  implements the interface and holds another component.
- **Tradeoffs.** Many small wrappers, order-sensitive behavior, deeper stack
  traces, and an interface that must remain stable.
- **Common misuse.** Decorating to compensate for a bad interface, nesting
  wrappers without documenting order, or using a decorator when a plain
  higher-order operation is enough.
- **Related SOLID.** OCP, LSP, DIP.
- **Sketch.**

```text
interface Reader { read() }
FileReader implements Reader
BufferedReader(inner: Reader).read() -> inner.read() with buffering
LoggingReader(inner: Reader).read() -> log; inner.read()
```

## Repository

- **Intent.** Present domain-oriented collection access while hiding persistence
  mechanics.
- **Problem / force.** Domain logic needs persisted data, storage details vary,
  and domain tests should not require a database or ORM.
- **Use when.** A real domain/persistence boundary exists, access is organized
  around aggregates, storage should be replaceable, or domain tests need a fake.
- **Avoid when.** The application is simple CRUD, the ORM model is the project's
  established domain model, or the repository would only mirror every query.
  Reporting and read-model queries usually belong closer to their consumer.
- **Structure.** A repository interface owned by the domain or application
  layer; an infrastructure implementation; domain types and explicit mapping.
- **Tradeoffs.** Mapping overhead, queries hidden behind methods, risk of
  inefficient access, and transaction boundaries that need a separate decision.
- **Common misuse.** A repository per table, returning ORM entities, a generic
  `BaseRepository`, or using the repository as a query DSL.
- **Default stance.** Use a repository when it protects a domain/persistence
  boundary, not as a mandatory layer over every query.
- **Related SOLID.** DIP, SRP, ISP.
- **Sketch.**

```text
interface OrderRepository { save(order); byId(id); openOrders() }
SqlOrderRepository implements OrderRepository  // infrastructure
PlaceOrder(repository: OrderRepository)        // application depends on the port
```

## Singleton

- **Intent.** Ensure one instance exists and provide a controlled access point.
- **Problem / force.** A genuinely shared resource with one process-wide
  lifecycle, such as a connection pool, cache, or configuration snapshot.
- **Use when.** A single instance is a real invariant, initialization is
  expensive or stateful, and the resource is truly global to the process.
- **Avoid when.** It is used for convenience, hides a dependency, breaks test
  isolation, or a request or tenant scope would be more correct.
- **Structure.** Private construction, lazy or eager initialization, a static
  accessor, and explicit thread-safety.
- **Tradeoffs.** Global mutable state, hidden coupling, test pollution,
  initialization-order issues, and concurrency hazards.
- **Common misuse.** Turning it into a service locator, storing mutable
  configuration, or using it to avoid passing dependencies.
- **Default stance.** Prefer a DI-managed single instance; avoid global mutable
  state. Use a singleton only for a true process-wide resource.
- **Related SOLID.** DIP risk, SRP.
- **Sketch.**

```text
class ConnectionPool {
  private static instance
  static get() -> create once, then return instance
}
```

## Factory

- **Intent.** Centralize creation choice and hide construction details.
- **Problem / force.** Callers should not know the concrete type, creation
  depends on configuration or input, or setup and validation are repeated.
- **Use when.** A family of related types shares a contract, creation logic is
  duplicated, callers need an interface, or implementations are registered and
  looked up.
- **Avoid when.** There is one concrete type with a simple constructor, or
  constructor injection already expresses the dependency clearly.
- **Structure.** A product interface, concrete products, a factory function or
  method, and the selection input.
- **Tradeoffs.** An extra layer, hidden dependencies, and a factory that can grow
  into a god object or a switch that changes for every new type.
- **Common misuse.** A factory for every object, static factories with global
  state, or returning concrete types that defeat the abstraction.
- **Related SOLID.** OCP, DIP, SRP.
- **Sketch.**

```text
interface Exporter { export(data) }
CsvExporter implements Exporter
JsonExporter implements Exporter
createExporter(format) -> CsvExporter | JsonExporter | error
```

## Builder

- **Intent.** Construct a complex object step by step, separating construction
  from representation.
- **Problem / force.** Many optional parts, ordering or validation rules,
  immutable results, or several representations of the same construction.
- **Use when.** Constructors telescope, configuration is conditional, tests need
  readable fixtures, or construction steps must be validated before use.
- **Avoid when.** There are only a few parameters, a plain options record is
  enough, or the builder would duplicate validation already in the type.
- **Structure.** A builder with step or fluent methods, an optional director, and
  a `build` operation that validates and returns an immutable result.
- **Tradeoffs.** Boilerplate, mutable intermediate state, validation timing, and
  encouragement to over-configure.
- **Common misuse.** A builder for two fields, `build` without validation, or
  sharing a mutable builder across threads.
- **Related SOLID.** SRP, OCP.
- **Sketch.**

```text
builder = RequestBuilder()
builder.method("POST").url("/orders").header("trace", id).body(payload)
request = builder.build()  // validates required parts
```

## Adapter

- **Intent.** Convert one interface into another expected by the client.
- **Problem / force.** A third-party, legacy, or platform API does not match the
  domain contract, and its types and errors should not spread inward.
- **Use when.** Integrating an external system, migrating a legacy API, wrapping
  an inconsistent vendor interface, or protecting the domain from vendor types.
- **Avoid when.** Both sides are under your control and the interface can simply
  be changed, or the translation is a trivial rename at one local call site.
- **Structure.** A target interface, the adaptee, and an adapter that implements
  the target by delegating and translating types, errors, and semantics.
- **Tradeoffs.** An extra layer, translation loss, error and type mapping, and
  maintenance when the vendor changes.
- **Common misuse.** Leaking vendor types through the adapter, using it to avoid
  fixing a bad boundary, or writing multiple adapters for the same vendor API.
- **Related SOLID.** DIP, SRP, LSP.
- **Sketch.**

```text
interface PaymentGateway { charge(amount, token) -> Receipt }
StripeAdapter implements PaymentGateway
  charge(amount, token) -> translate to Stripe call, map response and errors
```

## Chain of Responsibility

- **Intent.** Pass a request along a sequence of handlers until one handles it or
  all decline.
- **Problem / force.** Sequential validation, approval, or fallback steps vary,
  order matters, and the caller should not know the handler set.
- **Use when.** Multiple handlers may process a request, the chain is configured
  or ordered, and a handler can stop or pass control.
- **Avoid when.** Exactly one handler exists, a simple conditional is clear, or
  every layer must run. For cross-cutting layers that always run around a
  handler, use middleware; for many independent consumers, use events.
- **Structure.** A handler contract with a handle operation and a way to invoke
  the next handler; concrete handlers; explicit chain assembly.
- **Tradeoffs.** Implicit control flow, harder debugging, ordering coupling, and
  ambiguous behavior when no handler accepts the request.
- **Common misuse.** Using a chain for middleware, a handler that always handles,
  or a hidden global chain with no explicit assembly.
- **Related SOLID.** OCP, SRP, LSP.
- **Sketch.**

```text
interface Approver { approve(request, next) }
Manager.approve -> approve up to limit, else next
Director.approve -> approve up to limit, else next
chain = Manager -> Director -> Reject
```

## State

- **Intent.** Let an object change behavior when its internal state changes,
  making transitions explicit.
- **Problem / force.** A lifecycle has distinct states and legal transitions;
  conditionals on status spread across the code; invalid transitions are easy.
- **Use when.** States and transitions are central, behavior differs materially
  per state, and legal moves must be enforced in one place.
- **Avoid when.** There are two simple flags, state is just data, transitions are
  trivial, or a state-machine library already exists and is the better fit.
- **Structure.** A context delegates to a state object; concrete states implement
  behavior and transition rules; a transition table is optional.
- **Tradeoffs.** Class or type explosion, transition logic spread across states,
  persistence of state, and concurrency around transitions.
- **Common misuse.** State objects for simple enum branching, states with no
  behavior, or using State to avoid modeling a workflow explicitly.
- **Related SOLID.** OCP, SRP.
- **Default stance.** Prefer Strategy when the variant is selected from outside;
  use State only when transitions are central.
- **Sketch.**

```text
class Order {
  state: Draft | Paid | Shipped | Cancelled
  pay() -> state.pay(this)
}
Draft.pay -> transition to Paid
Paid.pay -> reject illegal transition
```

## Observer / Events

- **Intent.** Notify multiple interested consumers when something happens
  without the producer knowing them.
- **Problem / force.** One event triggers several independent reactions;
  consumers are added over time; producer and consumers should evolve separately.
- **Use when.** There are multiple independent consumers, the producer should not
  depend on them, or asynchronous delivery is acceptable and useful.
- **Avoid when.** There is one consumer, the reaction must be atomic with the
  producer's transaction, or ordering and delivery guarantees are undefined. A
  direct call is clearer for one consumer.
- **Structure.** A publisher exposes subscribe and publish; handlers implement a
  common contract or receive an event; dispatch happens at a clear boundary.
- **Tradeoffs.** Hidden control flow, ordering, duplication, retries, eventual
  consistency, error isolation, and subscription lifecycle leaks.
- **Common misuse.** An event bus used as a global service locator, events used
  for commands, publishing inside a transaction without an outbox, or
  fire-and-forget without error handling.
- **Default stance.** Use events for genuine decoupling, not as the default way
  to call code.
- **Related SOLID.** OCP, DIP.
- **Sketch.**

```text
publisher.subscribe(handler)
publisher.publish(OrderPlaced { orderId })
handlers: reserveStock, sendReceipt, updateAnalytics
```

## Middleware

- **Intent.** Compose cross-cutting request processing around a handler in a
  defined order.
- **Problem / force.** Authentication, logging, tracing, recovery, CORS, or rate
  limiting applies to many endpoints and must be applied consistently.
- **Use when.** Cross-cutting behavior applies to a request pipeline, order is
  explicit, and a layer may short-circuit or enrich the request.
- **Avoid when.** There is a single handler, the behavior is business logic, or
  no pipeline concept exists in the project.
- **Structure.** A handler signature, middleware that wraps the next handler, and
  explicit chain assembly at the transport boundary.
- **Tradeoffs.** Hidden control flow, ordering coupling, error handling, scope
  creep, and framework coupling.
- **Common misuse.** Business rules in middleware, global middleware for one
  route, or undocumented ordering that changes behavior.
- **Related SOLID.** OCP, SRP.
- **Sketch.**

```text
handler = recover(logging(auth(routeHandler)))
middleware(next) -> handler that runs its concern, then next
```

## Value Object

- **Intent.** Model an immutable domain concept by its values and invariants, not
  by identity.
- **Problem / force.** Primitive obsession, repeated validation, equality by
  value, units, currency, email addresses, or identifiers with rules.
- **Use when.** The concept has invariants or behavior, a primitive can be
  invalid, equality is by value, or immutability prevents accidental sharing.
- **Avoid when.** The concept has identity and a lifecycle (use an entity), there
  are no invariants, or the value is a purely local variable.
- **Structure.** Immutable fields, validation in construction, value equality,
  no setters, and operations that return new values.
- **Tradeoffs.** Allocation, ORM mapping, serialization boundaries, and
  over-modeling simple data.
- **Common misuse.** An anemic wrapper with no validation, a mutable value
  object, or a value object that secretly carries identity.
- **Related SOLID.** SRP, LSP.
- **Sketch.**

```text
record Money(amount, currency) {
  constructor -> reject negative amount or missing currency
  plus(other) -> new Money if currencies match
}
```

## Unit of Work

- **Intent.** Track changes and commit them as one transaction.
- **Problem / force.** Multiple repository operations must be atomic, changes
  need coordination, or one transaction boundary spans several aggregates.
- **Use when.** Real transactional consistency is required, rollback matters,
  the ORM already provides change tracking, or the application service owns the
  transaction.
- **Avoid when.** There is a single write, operations are independent, the
  storage has no transaction support, or it is added only "for consistency".
- **Structure.** A unit of work tracks new, dirty, and removed objects, exposes
  commit and rollback, and binds repositories to the same session.
- **Tradeoffs.** Complexity, hidden flushes, long transactions, concurrency
  concerns, and heavier test setup.
- **Common misuse.** A unit of work around every request with no transaction,
  leaking the ORM session, or mixing it with repositories that commit on their
  own.
- **Default stance.** Use a unit of work when transaction boundaries or change
  tracking are real requirements.
- **Related SOLID.** SRP, DIP.
- **Sketch.**

```text
unit = unitOfWork()
orders = unit.repository(OrderRepository)
orders.save(order)
unit.commit()  // one transaction, or rollback on failure
```

## Dependency Injection

- **Intent.** Supply dependencies from outside instead of constructing or
  locating them internally.
- **Problem / force.** Testability, decoupling from implementations, lifecycle
  management, configuration, or the need to swap an implementation.
- **Use when.** A real boundary exists, tests need fakes, multiple
  implementations are plausible, or wiring should be centralized.
- **Avoid when.** The object is a trivial value, the dependency is stable and
  local, or a container adds indirection without solving a real problem.
- **Structure.** Constructor or parameter injection; a composition root that
  wires concrete types; a container only when it earns its keep.
- **Tradeoffs.** Wiring complexity, lifetime bugs, harder navigation, and
  container magic that obscures construction.
- **Common misuse.** Service locator, injecting everything, putting the container
  in the domain, or using DI to avoid making a design decision.
- **Default stance.** Treat dependency injection as a wiring principle, not a
  framework requirement.
- **Related SOLID.** DIP, SRP, ISP.
- **Sketch.**

```text
PlaceOrder(orders: OrderRepository, payments: PaymentGateway, clock: Clock)
main() -> PlaceOrder(SqlOrderRepository(db), StripeAdapter(client), systemClock)
```
