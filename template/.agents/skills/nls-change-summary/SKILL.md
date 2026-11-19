---
name: nls-change-summary
description: Write a high-level change summary of a finished feature or fix for the PR description, so the human reviewer knows what changed, how it differs from the approved plan, and where to read closely. Use when the developer asks for a change summary, PR summary, PR description, review guide or "describe the changes", or when implementation is done and a pull request is about to be opened.
---

# Change summary for review

Write a summary that lets the reviewer understand an agent-made change without reading every line, and tells them where they still should. The reviewer reads this before the diff, so it decides where their attention goes.

The summary is for the reviewer, not a record of the work. A uniform, padded summary quickly stops being read; a short one that points at the two places that matter keeps being read. Leave out anything the reviewer would not act on.

## Describe the code, not the intention

Base every statement on the diff, not on what you remember setting out to do. A summary written from memory describes the plan; the reviewer needs to know what the code actually does, including where it ended up differing.

If this session also wrote the code, re-read the diff before writing and check each claim against it. Tell the developer once, in a line outside the summary, that a fresh session gives a more independent summary.

Never claim something was verified unless you saw it happen in this session (for example a test run whose output you saw). Manual testing in QGIS or the test environment is the developer's to report: leave a marked placeholder for it.

## Gather the inputs

1. **The diff against the base branch.** Find the base with `git merge-base HEAD origin/main` (use the repo's default branch if it is not `main`), then read `git diff --stat <base>...HEAD` and `git diff <base>...HEAD`. Include staged and unstaged changes if there are no commits yet.
2. **The approved plan and acceptance criteria.** Use the plan from this conversation, a plan file the developer names, or the ticket. If none is available, ask the developer for it once; if they have none, write "No plan available" in the deviations section rather than inventing one.
3. **Test changes.** Note new tests, and separately any change to an existing test or expected value.

## Classify each change

Group the changes by purpose, not by file. A group is something like "New rule for lifecycle 2" or "Rename `geom_col` to `geometry`", and may span several files and repos.

Give each group one reading mode, based on what an error there would cost:

| Reading mode | Use for |
| --- | --- |
| **Read closely** | Database migrations; spatial queries, rules and other domain logic; authentication, permissions and data deletion; Ansible, Jenkins, container and deployment config; public APIs, schemas, shared helpers and config keys; new or changed dependencies; agent instruction and skill files |
| **Check** | Tests (do the assertions verify the criteria?); new logic that follows an existing pattern |
| **Skim** | Mechanical changes (renames, moved files, formatting); QML styles and symbols the tester will verify visually; documentation and comments |

Put mechanical changes in their own group so the reviewer can skim them in one go. If mechanical and behavioural changes are mixed in the same hunks, say so: it makes the review harder, and the developer may want to split them.

## Decide whether a diagram helps

Add one Mermaid diagram only when the change alters a structure the reviewer would otherwise have to reconstruct in their head:

- **Sequence diagram** when the flow between components changes, for example API, Airflow DAG, database and QGIS plugin.
- **ER diagram, before and after,** when tables, columns or relations change.
- **Flowchart** when branching logic in a rule or process changes.

Skip the diagram for changes inside a single function, mechanical changes and styling. Keep it under about 12 nodes, use the names that appear in the code, and draw only the changed part with enough context to place it. A diagram that repeats the file list adds nothing.

## Output

Write the summary in Markdown, ready to paste into the PR description. Omit any section that would be empty, except **Deviations from the plan**, where "None" is useful information. Aim for under 60 lines excluding the diagram.

```markdown
## Summary
[2–4 sentences: what changed and why, with the ticket reference. Behaviour, not files.]

## Deviations from the plan
[What differs from the approved plan and why. "None" if nothing differs.]

## Reading order
1. **[Group name]** — Read closely — `path/to/file.py` L40–95, `migrations/0042_x.py`
   [One line: what this group does and what could go wrong if it is wrong.]
2. **[Group name]** — Check — `tests/test_x.py`
   [One line.]
3. **[Mechanical changes]** — Skim — 6 files
   [One line: what kind of mechanical change.]

## Where to look
[The 1–3 specific spots most likely to be wrong, and the decisions you were unsure about. Be concrete: "the SRID transform in `to_geojson()` assumes input is EPSG:3067".]

## Verification
| Acceptance criterion | How verified |
| --- | --- |
| [criterion] | [test name, or **Developer to confirm: manual test**] |

Existing tests changed: [list with the reason for each, or "None"]

## Dependencies and risk areas
[New or changed dependencies and why each is needed; read-closely areas touched. Omit if none.]

## Diagram
[Mermaid diagram, only if the rules above call for one.]
```

After writing the summary, ask the developer to check it against their understanding of the change. If they cannot confirm a statement in it, that part of the change needs their attention before review.

## Example

A short summary for a small change:

```markdown
## Summary
Adds rule QR-118: features with attribute-1 value 2 must have attribute-2 value 2 (PPT-2231).

## Deviations from the plan
None.

## Reading order
1. **New rule definition** — Read closely — `rules/qr_118.yaml`
   Maps to the existing attribute-equality SQL template; a wrong parameter silently passes all features.
2. **Rule tests** — Check — `tests/rules/test_qr_118.py`
   One passing and two failing fixtures.

## Where to look
The rule treats NULL attribute-1 as a violation. The ticket does not say; existing rule QR-097 does the same.

## Verification
| Acceptance criterion | How verified |
| --- | --- |
| Attribute-1 value 2 with attribute-2 ≠ 2 is reported | `test_qr_118_reports_mismatch` |
| Other attribute-1 values are not affected | `test_qr_118_ignores_other_states` |

Existing tests changed: None
```
