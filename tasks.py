import datetime
import os
import shutil
import subprocess
import tomllib

from colorama import Fore, init
from invoke import task


def get_docker_compose_command():
    """
    `docker-compose` is the preferred command,
    but if it's not available, we fall back to `docker compose`
    """
    if shutil.which("docker-compose"):
        return "docker-compose"
    elif shutil.which("docker"):
        return "docker compose"
    else:
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=None,
            output=b"",
            stderr=b"Neither 'docker-compose' nor 'docker' executable found in the system path",
        )


@task
def db_snapshot(c, filename_prefix):
    """Create a Database snapshot using DSLR"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    (
        c.run(
            "dslr snapshot {filename_prefix}_{timestamp}".format(
                filename_prefix=filename_prefix,
                timestamp=timestamp,
            ),
            pty=True,
        ),
    )


@task(help={"build": "Build images before starting containers."})
def up(c, build=False):
    """docker-compose up -d"""
    docker_compose = get_docker_compose_command()
    if build:
        c.run(
            f"{docker_compose} -f docker-compose.yml up -d --build",
            pty=True,
        )
    else:
        c.run(f"{docker_compose} -f docker-compose.yml up -d", pty=True)


@task
def exec(c, container, command):
    """docker-compose exec [container] [command(s)]"""
    docker_compose = get_docker_compose_command()
    c.run(f"{docker_compose} exec {container} {command}", pty=True)


@task(help={"follow": "Follow log output"})
def logs(c, container, follow=False):
    """docker-compose logs [container] [-f]"""
    docker_compose = get_docker_compose_command()
    if follow:
        c.run(f"{docker_compose} logs {container} -f", pty=True)
    else:
        c.run(f"{docker_compose} logs {container}", pty=True)


@task
def stop(c):
    """docker-compose stop"""
    docker_compose = get_docker_compose_command()
    c.run(f"{docker_compose} stop", pty=True)


@task(
    help={
        "volumes": "Remove named volumes declared in the `volumes` section of the Compose file and anonymous volumes attached to containers."
    }
)
def down(c, volumes=False):
    """docker-compose down"""
    docker_compose = get_docker_compose_command()
    if volumes:
        c.run(f"{docker_compose} down -v", pty=True)
    else:
        c.run(f"{docker_compose} down", pty=True)


@task(help={"dump_file": "The name of the dump file to import"})
def import_db_dump(c, dump_file):
    """
    Import a database dump into the database container

    1. Copy the dump file into the db container
    2. drop existing database
    3. create new database
    4. import dump file into database
    5. clean up
    """
    # Extract filename from the dump_file path
    dump_filename = os.path.basename(dump_file)

    # copy dump file into db container
    c.run(f"docker cp {dump_file} zednews-db-1:/tmp/{dump_filename}", pty=True)
    # drop existing database
    c.run(
        'inv exec db "dropdb --if-exists --host db --username=zednews_dev_user zednews_dev_db"',
        pty=True,
    )
    # create new database
    c.run(
        'inv exec db "createdb --host db --username=zednews_dev_user zednews_dev_db"',
        pty=True,
    )
    # import dump file into database
    c.run(
        f'inv exec db "pg_restore --clean --no-acl --if-exists --no-owner --host db --username=zednews_dev_user -d zednews_dev_db /tmp/{dump_filename}"',
        pty=True,
    )
    # clean up
    c.run(f'inv exec db "rm -vf /tmp/{dump_filename}"', pty=True)


@task
def init_db(c):
    """use aerich to generate schema and generate app migrate location"""
    c.run("aerich init-db", pty=True)


@task
def migrate(c):
    """use aerich to update models and generate migrate changes file

    This is like django's makemigrations command
    """
    c.run("aerich migrate", pty=True)


@task
def upgrade(c):
    """use aerich to upgrade db to latest version

    This is like django's migrate command
    """
    c.run("aerich upgrade", pty=True)


@task(help={"fix": "let black and ruff format your files"})
def lint(c, fix=False):
    """ruff and black"""

    if fix:
        c.run("black .", pty=True)
        c.run("ruff check --fix .", pty=True)
    else:
        c.run("black . --check", pty=True)
        c.run("ruff check .", pty=True)


# TODO: create a "clean" collection comprising the next two tasks below


@task
def clean_pyc(c):
    """remove Python file artifacts"""

    c.run("find . -name '*.pyc' -exec rm -f {} +", pty=True)
    c.run("find . -name '*.pyo' -exec rm -f {} +", pty=True)
    c.run("find . -name '__pycache__' -exec rm -fr {} +", pty=True)
    c.run("find . -name '.ruff_cache' -exec rm -fr {} +", pty=True)
    c.run('find . -type d -name "*.egg-info" -exec rm -fr {} +', pty=True)


@task
def clean_test(c):
    """remove test and coverage artifacts"""

    c.run("rm -fr .tox/", pty=True)
    c.run("rm -f .coverage", pty=True)
    c.run("rm -f coverage.*", pty=True)
    c.run("rm -fr htmlcov/", pty=True)
    c.run("rm -fr .pytest_cache", pty=True)


def create_release(c, branch, is_first_release=False, push=False):
    """Create a release by combining `commitizen-tools` and `commit-and-tag-version`

    commitizen-tools works best with Python projects, but I don't like the
    generated changelogs. I had no time to look at how to customize them, so I
    decided to use commit-and-tag-version (which works best with Node.js projects).
    Unfortunately, commit-and-tag-version by default doesn't work with Python projects,
    and since I didn't have time to write my own updater for python files and toml files,
    I have to make the two work together!

    This requires commit-and-tag-version to be installed in your project:
    ``npm i -D commit-and-tag-version``

    The logic is as follows:

    1. cz bump --files-only
    2. git add pyproject.toml and other_files specified in pyproject.toml
    3. commit-and-tag-version --commit-all --release-as <result from cz if not none>
    4. git push --follow-tags origin [branch]
    """
    if is_first_release:  # tag a release without bumping the version bumpFiles
        with open("pyproject.toml", "rb") as f:
            toml_dict = tomllib.load(f)
        project = toml_dict["tool"]["poetry"]["name"]
        print(f"{Fore.YELLOW}Generating your changelog for your first release ...{Fore.RESET}")
        c.run(
            f'npm run release -- --first-release --releaseCommitMessageFormat "chore: This is {project} v{{{{currentTag}}}} 🎉"',
            pty=True,
        )
        if push:
            # push to origin
            c.run(f"git push --follow-tags origin {branch}", pty=True)
    else:
        print(f"{Fore.MAGENTA}Attempting to bump using commitizen-tools ...{Fore.RESET}")
        c.run("cz bump --files-only > .bump_result.txt", pty=True)
        str_of_interest = "increment detected: "
        result = ""
        with open(".bump_result.txt", "r") as br:
            for line in br:
                if str_of_interest in line:
                    result = line
                    break
        release_type = result.replace(str_of_interest, "").strip("\n").lower()
        print(f"cz bump result: {release_type}")
        if release_type == "none":
            print(f"{Fore.YELLOW}No increment detected, cannot bump{Fore.RESET}")
        elif release_type in ["major", "minor", "patch"]:
            print(f"{Fore.GREEN}Looks like the bump command worked!{Fore.RESET}")
            print(f"{Fore.GREEN}Now handing over to commit-and-tag-version ...{Fore.RESET}")
            # first, stage the bumped files
            with open("pyproject.toml", "rb") as f:
                toml_dict = tomllib.load(f)
            version_files = toml_dict["tool"]["commitizen"]["version_files"]
            files_to_add = " ".join(version_files)
            c.run(
                f"git add pyproject.toml {files_to_add}",
                pty=True,
            )
            # now we can pass result to standard-release
            print(f"{Fore.GREEN}let me retrieve the tag we're bumping from ...{Fore.RESET}")
            get_current_tag = c.run(
                "git describe --abbrev=0 --tags `git rev-list --tags --skip=0  --max-count=1`",
                pty=True,
            )
            previous_tag = get_current_tag.stdout.rstrip()

            c.run(
                f'npm run release -- --commit-all --release-as {release_type} --releaseCommitMessageFormat "bump: ✈️ {previous_tag} → v{{{{currentTag}}}}"',
                pty=True,
            )
            if push:
                # push to origin
                c.run(f"git push --follow-tags origin {branch}", pty=True)
        else:
            print(f"{Fore.RED}Something went horribly wrong, please investigate & fix it!{Fore.RESET}")
            print(f"{Fore.RED}Bump failed!{Fore.RESET}")

        # clean up
        c.run("rm -vf .bump_result.txt", pty=True)


@task(
    help={
        "branch": "The branch against which you wanna bump",
        "first": "Is this the first release?",
    }
)
def bump(c, branch, first=False):
    """Use Commitizen Tools & commit-and-tag-version to bump version and generate changelog

    Run this task when you want to prepare a release.
    First we check that there are no unstaged files before running
    """

    init()

    unstaged_str = "not staged for commit"
    uncommitted_str = "to be committed"
    check = c.run("git status", pty=True)
    if unstaged_str not in check.stdout or uncommitted_str not in check.stdout:
        create_release(c, branch, first, push=False)
    else:
        print(f"{Fore.RED}Sorry mate, please ensure there are no unstaged files before creating a release{Fore.RESET}")


@task
def get_release_notes(c):
    """extract content from CHANGELOG.md for use in Github Releases

    we read the file and loop through line by line
    we wanna extract content beginning from the first Heading 2 text
    to the last line before the next Heading 2 text
    """

    pattern_to_match = "## [v"

    count = 0
    lines = []
    heading_text = "## What's changed in this release\n"
    lines.append(heading_text)

    with open("CHANGELOG.md", "r") as c:
        for line in c:
            if pattern_to_match in line and count == 0:
                count += 1
            elif pattern_to_match not in line and count == 1:
                lines.append(line)
            elif pattern_to_match in line and count == 1:
                break

    # home = str(Path.home())
    # release_notes = os.path.join(home, "LATEST_RELEASE_NOTES.md")
    release_notes = os.path.join("../", "LATEST_RELEASE_NOTES.md")
    with open(release_notes, "w") as f:
        print("".join(lines), file=f, end="")


@task
def digest(c):
    """Generate news digest from latest Zambian news sources"""
    c.run("python app/core/run.py", pty=True)


@task
def test(c):
    """run tests"""
    c.run("coverage run -m unittest discover app/tests", pty=True)
    c.run("coverage json", pty=True)
    c.run("coverage report -m", pty=True)


@task
def fx_update(c):
    """Update foreign exchange rates data"""
    c.run("python -m app.core.fx.update", pty=True)


@task
def facebook_post(c):
    """Post to Facebook"""
    c.run("python -m app.core.social.post", pty=True)
