import os
import subprocess
from pathlib import Path

from launcher.commands.clear import clear as clear_db
from launcher.commands.update import update
from launcher.skyportal import patch as patch_skyportal


def build(
    init: bool = False,
    repo: str = "origin",
    branch: str = "main",
    do_update: bool = False,
    clear: bool = False,
    update_prod: bool = False,
    skip_services_check: bool = False,  # not used here
):
    """Build Icare
    :param init: Initialize Icare
    :param repo: Remote repository to pull from
    :param do_update: pull <repo>/<branch>, autostash SP and update submodules
    :param clear: Clear the database
    """
    # if previous_skyportal directory doesnt exist, create it and copy the skyportal files in it
    previous_skyportal_dir = Path("previous_skyportal")
    if not previous_skyportal_dir.exists():
        previous_skyportal_dir.mkdir()
        cmd = subprocess.Popen(["cp", "-a", "skyportal/.", "previous_skyportal/"])
        cmd.wait()

    new_changes = False
    skyportal_start = True
    if do_update:
        new_changes, skyportal_start = update(repo=repo, branch=branch)
    if update_prod:
        print("Stamping current database state")
        cmd = subprocess.Popen(
            ["alembic", "-x", "config=config.yaml", "stamp", "head"],
            cwd="patched_skyportal",
        )
        cmd.wait()
        print("Updating submodules")
        cmd = subprocess.Popen(["git", "submodule", "update", "--init", "--recursive"])
        cmd.wait()
    # if patched_skyportal directory exists, patch it
    patched_skyportal_dir = Path("patched_skyportal")
    exists = patched_skyportal_dir.exists()
    if not exists:
        patched_skyportal_dir.mkdir()

    if new_changes or not exists or update_prod:
        # copy skyportal to patched_skyportal
        cmd = subprocess.Popen(["cp", "-a", "skyportal/.", "patched_skyportal/"])
        cmd.wait()
        cmd = subprocess.Popen(["rm", "-rf", "patched_skyportal/.git"])
    else:
        print(
            "\nNo changes detected, not copying skyportal to patched_skyportal, but still patching it"
        )

    patch_skyportal("extensions/skyportal/", "patched_skyportal/")

    # Remove stale .js files that were converted to .ts in skyportal.
    # When patched_skyportal is populated by copying skyportal/, old .js files
    # from a previous build are not deleted — only overwritten if still present.
    # Any .js file no longer in the skyportal source is a leftover that conflicts
    # with its .ts replacement at bundle time.
    js_root = Path("patched_skyportal/static/js")
    sp_js_root = Path("skyportal/static/js")
    if js_root.exists() and sp_js_root.exists():
        for js_file in js_root.rglob("*.js"):
            rel = js_file.relative_to("patched_skyportal")
            if not (sp_js_root.parent.parent / rel).exists():
                print(f"Removing stale JS file: {js_file}")
                js_file.unlink()

    if clear and skyportal_start:
        clear_db()

    if init and skyportal_start:
        # run the command make run in skyportal dir
        env = os.environ.copy()
        env["NPM_CONFIG_LEGACY_PEER_DEPS"] = "true"
        cmd = subprocess.Popen(["make", "db_init"], cwd="patched_skyportal")
        cmd.wait()

    return skyportal_start
