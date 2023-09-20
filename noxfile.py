"""Development tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import nox

FILES: list[str] = ['src', 'tests', 'docs', 'noxfile.py']
CHANGELOG_ARGS: dict[str, Any] = {
    'repository': '.',
    'convention': 'angular',
    'template': 'keepachangelog',
    'parse_trailers': True,
    'parse_refs': False,
    'sections': ['feat', 'fix', 'docs', 'style', 'refactor', 'tests', 'chore'],
    'bump_latest': True,
    'output': 'CHANGELOG.md',
}


def check_cli(session: nox.Session, args: list[str]) -> None:
    """Check the CLI arguments.

    Arguments:
        session: The nox session.
        args: The available CLI arguments.
    """
    available_args = ', '.join([f'`{arg}`' for arg in args])
    msg = f'Available subcommands are one of {available_args}.'
    if not session.posargs:
        session.skip(f'{msg} No subbcommand was provided')
    elif len(session.posargs) > 1 or session.posargs[0] not in args:
        session.skip(f'{msg} Instead `{" ".join(session.posargs)}` was given')


@nox.session
def docs(session: nox.Session) -> None:
    """Build or serve the documentation.

    Arguments:
        session: The nox session.
    """
    check_cli(session, ['serve', 'build'])
    session.run('mkdocs', session.posargs[0])


@nox.session
@nox.parametrize('file', FILES)
def formatting(session: nox.Session, file: str) -> None:
    """Format the code.

    Arguments:
        session: The nox session.
        file: The file to be formatted.
    """
    check_cli(session, ['all', 'code', 'docstrings'])
    if session.posargs[0] in ['code', 'all']:
        session.run('black', file)
    if session.posargs[0] in ['docstrings', 'all']:
        session.run('docformatter', '--in-place', '--recursive', '--close-quotes-on-newline', file)


@nox.session
@nox.parametrize('file', FILES)
def checks(session: nox.Session, file: str) -> None:
    """Check code quality, dependencies or type annotations.

    Arguments:
        session: The nox session.
        file: The file to be checked.
    """
    check_cli(session, ['all', 'quality', 'dependencies', 'types'])
    if session.posargs[0] in ['quality', 'all']:
        session.run('ruff', file)
    if session.posargs[0] in ['types', 'all']:
        session.run('mypy', file)
    if session.posargs[0] in ['dependencies', 'all']:
        requirements_path = (Path(session.create_tmp()) / 'requirements.txt').as_posix()
        args_groups = [['--prod']] + [['-dG', group] for group in ['tests', 'docs', 'maintenance']]
        requirements_types = zip(FILES, args_groups, strict=True)
        args = [
            'pdm',
            'export',
            '-f',
            'requirements',
            '--without-hashes',
            '--no-default',
            '--pyproject',
            '-o',
            requirements_path,
        ]
        session.run(*(args + dict(requirements_types)[file]), external=True)
        session.run('safety', 'check', '-r', requirements_path)


@nox.session
def tests(session: nox.Session) -> None:
    """Run tests and coverage.

    Arguments:
        session: The nox session.
    """
    env = {'COVERAGE_FILE': f'.coverage.{session.python}'}
    if session.posargs:
        session.run('pytest', '-n', 'auto', '-k', *session.posargs, 'tests', env=env)
    else:
        session.run('pytest', '-n', 'auto', 'tests', env=env)
    session.run('coverage', 'combine')
    session.run('coverage', 'report')
    session.run('coverage', 'html')


@nox.session
def changelog(session: nox.Session) -> None:
    """Build the changelog.

    Arguments:
        session: The nox session.
    """
    from git_changelog.cli import build_and_render

    build_and_render(**CHANGELOG_ARGS)


@nox.session
def release(session: nox.Session) -> None:
    """Kick off a release process.

    Arguments:
        session: The nox session.
    """
    from git_changelog.cli import build_and_render

    changelog, _ = build_and_render(**CHANGELOG_ARGS)
    version = changelog.versions_list[0].planned_tag
    if version is None:
        version = changelog.versions_list[0].tag

    # Create release branch and commit changelog
    session.run('git', 'checkout', '-b', f'release_{version}', external=True)
    session.run('git', 'add', 'CHANGELOG.md', external=True)
    session.run('git', 'commit', '-m', f'chore: Release {version}', '--allow-empty', external=True)
    session.run('git', 'push', '-u', 'origin', f'release_{version}', external=True)

    # Create and merge PR from release branch to main
    session.run('gh', 'pr', 'create', '--base', 'main', external=True)
    session.run('gh', 'pr', 'merge', '--rebase', '--delete-branch', external=True)

    # Create tag
    session.run('git', 'checkout', 'main', external=True)
    session.run('git', 'pull', '--rebase', external=True)
    session.run('git', 'tag', version, external=True)
    session.run('git', 'push', '--tags', external=True)

    # Build and upload artifacts
    session.run('pdm', 'build', external=True)
    session.run('twine', 'upload', '--skip-existing', 'dist/*')
