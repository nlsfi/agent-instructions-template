# AI agent skills used in National Land Survey repositories

Common reusable skills for repositories that use AI coding agents.
Copier manages conditional skill installation.

## Using this template

### Initial setup for a repo

Run `copier copy` from the target repository root and answer the prompts:

```
copier copy --answers-file .copier-answers.agent-instructions.yml https://github.com/nlsfi/agent-instructions-template.git .
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
copier update --answers-file .copier-answers.agent-instructions.yml
```

Copier diffs the new template against the previous version and proposes
changes; review and accept as needed.

### Adding a new module to an existing repo

Re-run `copier update` and set the new module flag to `true` when prompted.
Then add or update routing hints in the repo's `AGENTS.md` so agents load the
right skill explicitly for high-risk domains.

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
