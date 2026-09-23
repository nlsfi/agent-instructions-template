"""
Copier post-generation task (invoked from copier.yml's `_tasks`). Vendors
selected external Agent Skills (SKILL.md folders) from curated third-party
repos into .agents/skills/<folder>/<name>/ in the consumer repo, pinned to a
specific ref, and writes a human-readable manifest.

Reads:
  - <this template repo>/external-skills/registry.yml   (curated allow-list)
  - <consumer repo>/.agents/skills/vendor-selection.yml (rendered by copier
    from this run's answers - see template/.agents/skills/vendor-selection.yml.jinja)

Idempotent: safe to re-run via `copier update`. Existing vendored folders
are replaced wholesale, not merged - if a skill needs a local tweak, fork
it into your own skills tree under a different name rather than editing
the vendored copy in place, since edits will silently disappear on the
next update.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

# scripts/vendor_external_skills.py -> parent.parent == template repo root
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = TEMPLATE_ROOT / "external-skills" / "registry.yml"

# Copier runs _tasks with cwd == the destination (consumer repo) root.
DEST_ROOT = Path.cwd()
SELECTION_PATH = DEST_ROOT / ".agents" / "skills" / "vendor-selection.yml"
SKILLS_DIR = DEST_ROOT / ".agents" / "skills"
MANIFEST_PATH = SKILLS_DIR / "EXTERNAL_SKILLS.md"
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FOLDER_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def resolve_commit_sha(repo_dir: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def validate_registry(registry: dict) -> None:
    """Validate pins and ensure each folder has one source and license."""
    folder_metadata: dict[str, tuple[str, str]] = {}
    for name, entry in registry.items():
        ref = entry.get("ref") if isinstance(entry, dict) else None
        if not isinstance(ref, str) or not COMMIT_SHA_PATTERN.fullmatch(ref):
            print(
                f"::error:: Registry entry '{name}' has invalid ref {ref!r}; "
                "expected a 40-character lowercase commit SHA.",
                file=sys.stderr,
            )
            sys.exit(1)

        folder = entry.get("folder") if isinstance(entry, dict) else None
        if not isinstance(folder, str) or not FOLDER_NAME_PATTERN.fullmatch(folder):
            print(
                f"::error:: Registry entry '{name}' has invalid folder {folder!r}; "
                "expected one safe directory name.",
                file=sys.stderr,
            )
            sys.exit(1)

        metadata = (entry.get("repo"), entry.get("license"))
        previous = folder_metadata.get(folder)
        if previous is not None and previous != metadata:
            print(
                f"::error:: Registry folder '{folder}' mixes repositories or "
                f"licenses; use separate folders for '{name}'.",
                file=sys.stderr,
            )
            sys.exit(1)
        folder_metadata[folder] = metadata


def clone_at_ref(repo_url: str, ref: str, tmp_dir: Path) -> Path:
    """Fetch and check out exactly `ref`, with a full-clone fallback."""
    dest = tmp_dir / "src"
    dest.mkdir()
    subprocess.run(["git", "-C", str(dest), "init"], check=True,
                   capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(dest), "remote", "add", "origin", repo_url],
        check=True, capture_output=True, text=True,
    )
    shallow = subprocess.run(
        ["git", "-C", str(dest), "fetch", "--depth", "1", "origin", ref],
        capture_output=True, text=True,
    )
    if shallow.returncode == 0:
        subprocess.run(
            ["git", "-C", str(dest), "checkout", "--detach", "FETCH_HEAD"],
            check=True, capture_output=True, text=True,
        )
        return dest

    shutil.rmtree(dest)
    subprocess.run(["git", "clone", repo_url, str(dest)],
                    check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--detach", ref],
                    check=True, capture_output=True, text=True)
    return dest


def vendor_one(
    name: str,
    registry: dict,
    manifest_lines: list[str],
    license_folders: set[str],
) -> None:
    entry = registry.get(name)
    if entry is None:
        print(
            f"::error:: '{name}' is selected but not present in "
            f"external-skills/registry.yml - refusing to fetch an "
            f"unreviewed source. Add it to the registry first.",
            file=sys.stderr,
        )
        sys.exit(1)

    ref = entry["ref"]
    folder = entry["folder"]
    group_dir = SKILLS_DIR / folder
    target = group_dir / name
    print(
        f"Vendoring '{name}' from {entry['repo']} @ {ref} "
        f"({entry.get('ref_label', 'unlabeled')}) -> {target}"
    )

    with tempfile.TemporaryDirectory(prefix="vendor-skill-") as tmp:
        tmp_dir = Path(tmp)
        repo_dir = clone_at_ref(entry["repo"], ref, tmp_dir)
        resolved_sha = resolve_commit_sha(repo_dir)
        if resolved_sha != ref:
            print(
                f"::error:: Checked-out commit {resolved_sha} does not match "
                f"registry ref {ref} for '{name}'.",
                file=sys.stderr,
            )
            sys.exit(1)

        source_skill_dir = repo_dir / entry["subpath"]
        if not (source_skill_dir / "SKILL.md").exists():
            print(
                f"::error:: {entry['subpath']}/SKILL.md not found in "
                f"{entry['repo']} @ {ref} - registry entry may be stale.",
                file=sys.stderr,
            )
            sys.exit(1)

        group_dir.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        shutil.copytree(source_skill_dir, target, dirs_exist_ok=True)

        if folder not in license_folders:
            license_file = repo_dir / "LICENSE"
            if license_file.exists():
                shutil.copy(license_file, group_dir / "THIRD_PARTY_LICENSE")
            license_folders.add(folder)

    manifest_lines.append(
        f"| `{folder}/{name}` | {entry['repo']} | `{ref}` ({entry.get('ref_label', '')}; "
        f"resolved `{resolved_sha}`) "
        f"| {entry['license']} | {date.today().isoformat()} |"
    )


def write_manifest(manifest_lines: list[str]) -> None:
    header = (
        "# External Agent Skills\n\n"
        "Vendored copies of third-party Agent Skills. **Do not hand-edit "
        "the contents of `.agents/skills/<folder>/<name>/`** - changes are "
        "overwritten on the next `copier update`. To adjust a skill, "
        "propose the change upstream or fork it into your own skills "
        "tree under a different name.\n\n"
        "To change what's vendored, edit the `external_skills` answer and run:\n"
        "`copier update --trust --answers-file .copier-answers.agent-instructions.yml`\n\n"
        f"_Last vendored: {datetime.now(timezone.utc).isoformat(timespec='seconds')}_\n\n"
        "| Skill (folder/name) | Source | Pinned ref (resolved SHA) | License | Vendored on |\n"
        "|---|---|---|---|---|\n"
    )
    MANIFEST_PATH.write_text(header + "\n".join(manifest_lines) + "\n", encoding="utf-8")


def main() -> None:
    selection = load_yaml(SELECTION_PATH)
    skills = selection.get("skills") or []
    registry = load_yaml(REGISTRY_PATH)
    validate_registry(registry)

    if not skills:
        if MANIFEST_PATH.exists():
            print(
                "No external skills selected this run; leaving existing "
                "vendored folders in place; consumers can remove old or "
                "unselected .agents/skills/<folder>/<name>/ folders "
                "manually if no longer wanted)."
            )
        return

    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    manifest_lines: list[str] = []
    license_folders: set[str] = set()
    for name in skills:
        vendor_one(name, registry, manifest_lines, license_folders)

    write_manifest(manifest_lines)
    print(f"Vendored {len(skills)} external skill(s). See {MANIFEST_PATH}.")


if __name__ == "__main__":
    main()
