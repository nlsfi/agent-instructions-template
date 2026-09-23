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
`pyqgis-dev` and `qgis4-migration`.

Each registry entry pins a selected skill to a 40-character commit SHA and
includes a human-readable `ref_label`; consumers cannot override that pin.
Each registry entry also specifies a destination folder. Selected skills are
copied to `.agents/skills/<folder>/<name>/`, with one `THIRD_PARTY_LICENSE`
file per folder. The task fetches the exact registry commit and writes
`.agents/skills/EXTERNAL_SKILLS.md` with the destination, source repository,
pinned SHA, label, license, and vendoring date. A Git installation and network
access to the selected repositories are required. The current skills are
grouped under `.agents/skills/gispo-coding-pyqgis/`.

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
