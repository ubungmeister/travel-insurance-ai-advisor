# Project guidance

## Architecture and diagram requests
When the user explicitly asks to design or revise application architecture, use the project-scoped specialist agents under .codex/agents/ for independent read-only reviews:
- product_architect for goals, scope, user flows, and unknowns
- solution_architect for architecture options and trade-offs
- architecture_reviewer for an independent simplicity, privacy, and insurance-answering risk review
- diagram_architect to express the synthesized proposal as Mermaid diagrams

Keep the lead agent responsible for synthesis and user communication. Ask the specialists to cite repository paths for observed facts and label assumptions separately. Wait for independent reviews before synthesizing. Then have the diagram specialist produce draft diagrams from the synthesis; it must label unresolved choices rather than silently decide them.

For architecture work, do read-only discovery first. Present options, a recommendation, diagrams, risks, and open decisions for the user to correct or approve. Do not edit application code or begin implementation until the user explicitly approves. If the user asks to save a draft, limit changes to architecture documentation and report the exact files.
