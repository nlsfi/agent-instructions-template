# AI agent instructions used in National Land Survey repositories

Common instructions that can be used in all repositories that use AI agents.
Copier manages instruction templates.

## Using this template

### Initial setup for a repo

Run `copier copy` from the target repository root and answer the prompts:

```
copier copy --answers-file .copier-answers.agent-instructions.yml https://github.com/nlsfi/agent-instructions-template.git .
```

Copier writes the selected `agent-instructions/*.md` files and a
`.copier-answers.yml` that records your choices for future updates.

### Updating shared instructions

When the template is updated, pull the changes into the consumer repo:

```
copier update --answers-file .copier-answers.agent-instructions.yml
```

Copier diffs the new template against the previous version and proposes
changes; review and accept as needed.

### Adding a new module to an existing repo

Re-run `copier update` with the new flag set to `true` when prompted, or
copy the module file manually and add a link to the `## Module instructions`
section of the repo's `AGENTS.md`.

---

## Development environment

Create a virtual environment and install `pre-commit`:

```powershell
pip install pre-commit
pre-commit install
```
