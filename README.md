# AI agent skills used in National Land Survey repositories

Common reusable skills for repositories that use AI coding agents.
Copier manages conditional skill installation.

## Using this template

### Initial setup for a repo

Run `copier copy` from the target repository root and answer the prompts:

```
copier copy --trust --answers-file .copier-answers.agent-instructions.yml https://github.com/nlsfi/agent-instructions-template.git .
```

Copier writes selected skill files under `.agents/skills/` and a
`.copier-answers.yml` that records your choices for future updates.

Enabled modules render as:

- `.agents/skills/nls/python/SKILL.md`
- `.agents/skills/nls/java/SKILL.md`
- `.agents/skills/nls/sql/SKILL.md`
- `.agents/skills/nls/ansible/SKILL.md`
- `.agents/skills/nls/jenkins/SKILL.md`
- `.agents/skills/nls/qgis/SKILL.md`
- `.agents/skills/nls/airflow/SKILL.md`

Disabled modules do not create their corresponding module directory under
`.agents/skills/nls/`.

### Updating shared skills

When the template is updated, pull changes into the consumer repo:

```
copier update --trust --answers-file .copier-answers.agent-instructions.yml
```

Copier diffs the new template against the previous version and proposes
changes; review and accept as needed.

### Adding a new module to an existing repo

Re-run `copier update` and set the new module flag to `true` when prompted.
Then add or update routing hints in the repo's `AGENTS.md` so agents load the
right skill explicitly for high-risk domains.

### Vendoring external skills

During `copier copy` or `copier update`, set **Vendor curated external Agent
Skills** to `true` and select one or more skills. Only skills listed in the
template's curated allow-list at `external-skills/registry.yml` can be
fetched. The current choices include
`pyqgis-dev`, `qgis4-migration`, `ansible-good-practices`,
`ansible-new-molecule`, and `ansible-new-role`.

Each registry entry pins a selected skill to a 40-character commit SHA and
includes a human-readable `ref_label`; consumers cannot override that pin.
Each registry entry also specifies a destination folder. Selected skills are
copied to `.agents/skills/<folder>/<name>/`, with one `THIRD_PARTY_LICENSE`
file per folder. The task fetches the exact registry commit and writes
`.agents/skills/EXTERNAL_SKILLS.md` with the destination, source repository,
pinned SHA, label, license, and vendoring date. A Git installation and network
access to the selected repositories are required. The current skills are
grouped under `.agents/skills/gispo-coding-pyqgis/`.

Some upstream repos keep supporting material (e.g. a `references/`
directory) as a sibling of the skill folder rather than nested inside it.
A registry entry's optional `extra_paths` list (each item: `subpath` +
`dest`) vendors those sibling directories alongside `SKILL.md`, at
`.agents/skills/<folder>/<name>/<dest>/`. `EXTERNAL_SKILLS.md` annotates any
skill that vendored extra paths, e.g. `` `folder/name` (+references) ``.

The Ansible skills provide distinct workflows: `ansible-good-practices`
reviews existing automation, `ansible-new-molecule` scaffolds Molecule tests,
and `ansible-new-role` scaffolds a new role. The role skill can use
`ansible-creator` when installed and optionally uses the `ansible-know` MCP
server for module-aware task generation; it falls back to manual scaffolding
without those tools.

Vendored directories are replaced wholesale on the next `copier update`; do
not edit them in place. Fork a skill into a separately named local skill if
you need to customize it. Check the registry notes for related skills that
must be selected together, such as `qgis4-migration` and `pyqgis-dev`. The
task does not remove old or unselected directories; consumers can clean those
up separately.

### Optional shared-symlink distribution

If your organization maintains a shared skills repository, you can symlink
`.agents/skills/nls/*` directories into consumer repos instead of using Copier
for ongoing propagation.

---

## Development environment

Create a virtual environment and install `pre-commit`:

```powershell
pip install pre-commit
pre-commit install
```
