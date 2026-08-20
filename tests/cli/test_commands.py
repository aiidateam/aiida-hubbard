"""Tests for CLI commands."""

from __future__ import annotations

import subprocess

import click
import pytest

from aiida_hubbard.cli import cmd_root


def recurse_commands(command: click.Command, parents: list[str] = None):
    """Recursively return all subcommands that are part of ``command``.

    :param command: The click command to start with.
    :param parents: A list of strings that represent the parent commands leading up to the current command.
    :returns: A list of strings denoting the full path to the current command.
    """
    if isinstance(command, click.Group):
        for command_name in command.commands:
            subcommand = command.get_command(None, command_name)
            if parents is not None:
                subparents = parents + [command.name]
            else:
                subparents = [command.name]
            yield from recurse_commands(subcommand, subparents)

    if parents is not None:
        yield parents + [command.name]
    else:
        yield [command.name]


def test_commands_available():
    """Test that all expected commands are registered with the CLI."""
    expected = [
        ['aiida-hubbard'],
        ['aiida-hubbard', 'calculation'],
        ['aiida-hubbard', 'calculation', 'launch'],
        ['aiida-hubbard', 'calculation', 'launch', 'hp'],
        ['aiida-hubbard', 'workflow'],
        ['aiida-hubbard', 'workflow', 'launch'],
        ['aiida-hubbard', 'workflow', 'launch', 'hp-base'],
        ['aiida-hubbard', 'workflow', 'launch', 'hp-main'],
        ['aiida-hubbard', 'workflow', 'launch', 'hubbard'],
    ]
    assert sorted(recurse_commands(cmd_root)) == sorted(expected)


def test_commands_protocols():
    """Test that the protocols exposed by the CLI match those implemented by the work chains."""
    from aiida_hubbard.cli.utils.options import DEFAULT_PROTOCOL, PROTOCOLS
    from aiida_hubbard.workflows.hp.base import HpBaseWorkChain
    from aiida_hubbard.workflows.hp.main import HpWorkChain
    from aiida_hubbard.workflows.hubbard import SelfConsistentHubbardWorkChain

    for cls in (HpBaseWorkChain, HpWorkChain, SelfConsistentHubbardWorkChain):
        assert sorted(cls.get_available_protocols()) == sorted(PROTOCOLS)
        assert cls.get_default_protocol() == DEFAULT_PROTOCOL


@pytest.mark.parametrize('command', recurse_commands(cmd_root))
@pytest.mark.parametrize('help_option', ('--help', '-h'))
def test_commands_help_option(command, help_option):
    """Test the help options for all subcommands of the CLI.

    The usage of ``subprocess.run`` is on purpose because using :meth:`click.Context.invoke`, which is used by the
    ``run_cli_command`` fixture that should usually be used in testing CLI commands, does not behave exactly the same
    compared to a direct invocation on the command line. The invocation through ``invoke`` does not go through all the
    parent commands and so might not get all the necessary initializations.
    """
    result = subprocess.run(command + [help_option], check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert 'Usage:' in result.stdout
