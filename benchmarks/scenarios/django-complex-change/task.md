# Add request content negotiation helpers

Extend Django's HTTP request handling with the public method
`HttpRequest.get_preferred_type(media_types)`, a backwards-compatible way for a
view to choose the best response media type from a list of types it can
produce. The behavior must be driven by the request's `Accept` header and must
follow HTTP content-negotiation rules rather than treating the header as a
simple string comparison.

Requirements:

- `HttpRequest.get_preferred_type(media_types)` must accept an ordered iterable
  (including a one-shot generator) of offered media type strings. It returns
  the exact selected string from that iterable, or `None` when no offered type
  is acceptable; it must not return a newly formatted media type.
- Respect media ranges, quality values, specificity, and media-type
  parameters. A more preferred accepted range must win even when the offered
  types are in a different order. Precedence is, in order: highest valid
  quality, most specific matching range (including parameters), earliest
  occurrence of an equally ranked range in the header, then earliest offered
  item. Thus every tie has a deterministic result.
- Define these header outcomes: a missing `Accept` header means every offered
  type is acceptable and selects the first offered item; an empty header, or a
  header containing no valid media ranges, makes no type acceptable; malformed
  comma-separated entries are ignored while valid entries remain usable; a
  wildcard can match; and a valid `q=0` range explicitly rejects matching
  types. A specific `q=0` exclusion wins over a broader positive range (for
  example, `text/html;q=0, text/*;q=1` rejects HTML but permits other text
  types). None of these inputs may crash, and rejected types must not be
  selected.
- Keep existing request classes and existing request/response behavior
  compatible, including the existing `HttpRequest.accepts(media_type)` API.
  In particular, adding this method must not remove or change the established
  boolean behavior of `accepts()`.
- Integrate the feature consistently across the relevant HTTP request and
  utility code, with public tests and user-facing documentation following
  Django's established conventions.

Do not rely on a particular internal class or file layout. Preserve the
project's supported Python versions and coding conventions.
