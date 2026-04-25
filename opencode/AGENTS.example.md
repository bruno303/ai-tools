## AI Agent Cost / Token Discipline

Use the cheapest capable model for the task.

Default:
- Use GPT-5.3-Codex for implementation.
- Use GPT-5.4 Mini or low-reasoning variants for exploration, small edits, docs, lint fixes, and test adjustments.
- Use GPT-5.5 only for complex design, difficult debugging, final review, or high-risk changes. Always confirm with the user before use it.

Context rules:
- Search before reading files.
- Read only relevant sections.
- Avoid broad repository scans.
- Ignore generated/build/vendor directories.
- Keep changes minimal.
- Do not repeatedly re-open unchanged files.
- Do not paste full logs or full file contents.
- Summarize findings compactly before editing.

