# AGENTS.md

## Project overview

This repo is the Copier template source for the `Agent Skills` system used across NLS repositories.
The `template/` directory contains files that Copier copies and renders into a target repository;
those files are used by agents in the target repository, not as this repository's own instructions.
It produces per-technology `SKILL.md` files (`nls-python`, `nls-sql`, `nls-jenkins`, etc.) under
`.agents/skills/` in target repositories.

This repository and a Copier-generated target repository are separate contexts. This repository has
its own `AGENTS.md` for editing the template source. A target repository has its own root
`AGENTS.md` for editing that repository and may additionally receive generated instructions under
`.agents/skills/`. Do not add a `.agents/` directory at this repository's root just because it
appears in the generated target layout; the `.agents/` path under `template/` is Copier source.

## Template source versus target instructions

- Skills and other instruction files under `template/` are Copier source files only. They are never
  loaded or used as agent instructions while working in this repository; they are used only in
  target repositories after Copier renders them.
- When changing a generated skill or other Copier-managed output, edit the corresponding source
  file under `template/`. Do not create a rendered `.agents/` tree at this repository's root.
- In a target (consumer) repository, agents use that repository's root `AGENTS.md` and the
  rendered `.agents/skills/nls-*/` directories.

## Tech stack

- **Markdown** — all template content and architecture docs
- **YAML** — pre-commit and Copier configuration
- **pre-commit** (Python CLI) — sole build/lint tool; install via `pip install pre-commit`
- **pre-commit-hooks** v6.0.0 — whitespace, line-ending, and merge-conflict checks
- **gitlint** v0.19.1 — commit message linting (Conventional Commits)
- **Node 24.10.0** — declared as default language version for pre-commit (reserved for future hooks)

## Project structure

```text
agent-instructions-template/
├── .github/exploration/             ← Architecture decision records (not CI workflows)
├── template/                        ← Copier _subdirectory; copied/rendered into target repositories
│   ├── .copier-answers.yml.jinja    ← Records feature-flag answers in the consumer repo
│   └── .agents/skills/               ← Copier source for generated skill directories
│       ├── {% if has_python %}nls-python{% endif %}/SKILL.md.jinja
│       ├── {% if has_java %}nls-java{% endif %}/SKILL.md.jinja
│       ├── {% if has_sql %}nls-sql{% endif %}/SKILL.md.jinja
│       ├── {% if has_ansible %}nls-ansible{% endif %}/SKILL.md.jinja
│       ├── {% if has_jenkins %}nls-jenkins{% endif %}/SKILL.md.jinja
│       ├── {% if has_qgis %}nls-qgis{% endif %}/SKILL.md.jinja
│       ├── {% if has_airflow %}nls-airflow{% endif %}/SKILL.md.jinja
│       └── nls-ai-housekeeping/SKILL.md
├── external-skills/                  ← Curated allow-list for third-party skills
│   └── registry.yml                  ← Destination folder, source, commit pin, license, and notes
├── scripts/                          ← Copier task scripts
│   └── vendor_external_skills.py     ← Clones and vendors selected external skills
├── copier.yml                       ← Feature-flag questions; sets _subdirectory: template
├── .pre-commit-config.yaml          ← All linting hooks; frozen SHAs — update only via pre-commit autoupdate
├── .gitlint                         ← Conventional Commits rules enforced on every commit
├── .editorconfig                    ← Indentation and line-ending rules per file type
└── README.md                        ← Consumer usage and dev setup
```

New template module files go under `template/.agents/skills/` and use Jinja-conditional directory
names such as `{% if has_python %}nls-python{% endif %}`. Copier renders these source paths into
`.agents/skills/nls-*/` directories in target repositories, so disabled modules do not render their
directory or `SKILL.md` file. `nls-ai-housekeeping` is always rendered. The repository root
intentionally does not have an `.agents/` directory; do not create one there.
Temporary plans and resources go in `.github/exploration/`.

External skills are not Copier template files: `copier.yml` renders the
selected names into `template/.agents/skills/vendor-selection.yml`, and the
post-generation task uses the root `external-skills/registry.yml` to validate
and fetch the selected sources into the consumer repository. Each registry
entry must identify a repository, a 40-character lowercase commit `ref`, a
documentation-only `ref_label`, a safe destination `folder`, a skill
`subpath` containing `SKILL.md`, and the applicable license. Skills are
fetched into `.agents/skills/<folder>-<name>/`, where `folder` is the repo
prefix and `name` is the registry skill name. An upstream `LICENSE` is copied
to each skill directory as `THIRD_PARTY_LICENSE`; supporting paths are copied
alongside `SKILL.md`. All entries in one folder must use the same repository
and license; incompatible groupings are rejected and must use separate
folders. Keep dependency or setup information in `notes`.
Consumer repositories select skill names only; they cannot choose the version
to fetch.

## Module instructions routing

- Consumer repositories should keep explicit routing lines in their root `AGENTS.md`.
- Example: "When editing Python files, load `nls-python`; when editing Ansible roles, load `nls-ansible`."
- Add explicit routing for vendored skills when they are needed for a domain;
  for example, route PyQGIS work to `pyqgis-dev` and migration work to
  `qgis4-migration`.
- Follow registry notes for related skills. `qgis4-migration` refers to
  `pyqgis-dev` scripts by relative path, so select both together.
- Do not rely on auto-discovery alone for domains where missing the skill can cause regressions.

## Build and test commands

There is no application build or test suite. The pre-commit hooks are the quality gate.

One-time setup (from repo root):

```bash
pip install pre-commit
pre-commit install
```

Run all checks manually:

```bash
pre-commit run --all-files
```

Hooks that run on `pre-commit`:

- `trailing-whitespace` (Markdown linebreak extension preserved)
- `end-of-file-fixer`
- `mixed-line-ending` — enforces LF for all files; CRLF only for `.bat`
- `check-added-large-files`
- `check-merge-conflict`

Hook that runs on `commit-msg`:

- `gitlint` — enforces Conventional Commits format (see **Conventions** below)

## Conventions

**Commit messages (gitlint enforced):**

- Allowed types: `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `style`, `test`
- Title length: 10–72 characters
- The word immediately after `type:` must be lowercase (regex: `: [^A-Z]`)
- The word `wip` is banned in the title
- Body lines: max 80 characters

**Formatting (.editorconfig enforced):**

- YAML and Markdown: 2-space indent
- Python: 4-space indent
- SQL: 2-space indent
- All files UTF-8, LF, final newline; `.bat` files use CRLF

**No inline comments** in Markdown template files unless documenting a non-obvious Copier/Jinja behaviour.

## Do not modify

- Frozen commit SHAs in `.pre-commit-config.yaml` — only update via `pre-commit autoupdate`, not by hand
- `.github/exploration/` — treat as append-only reference material

## Known pitfalls

1. **PowerShell + Jinja path parts**: Copier template paths may contain Jinja expressions in directory
   names. In PowerShell, wrap such names in single quotes (e.g. `'{% if has_python %}python{% endif %}'`)
   to prevent `{}` being parsed as a script block.
2. **pre-commit not installed**: Hooks only run after `pre-commit install`. On a fresh clone, committing
   without running that command will bypass all checks silently.
3. **External skill updates are destructive by design**: The vendoring task replaces each selected
   `.agents/skills/<folder>-<name>/` directory wholesale. Do not hand-edit a vendored copy; fork it
   under a different name for local changes. Cleanup of old or unselected directories is the
   consumer's responsibility.
4. **External skill prerequisites**: Vendoring requires Git and network access. A stale registry entry
   fails when its configured `subpath/SKILL.md` cannot be found, and an unregistered skill is refused.
5. **External skill dependencies**: Select related skills together when a registry note requires it;
   vendoring one skill does not automatically vendor its dependencies.
