"""Fixtures for the command line interface."""

import pytest


@pytest.fixture
def filepath_cli_fixtures(filepath_tests):
    """Return the filepath of the directory containing the CLI test fixtures."""
    from pathlib import Path

    return Path(filepath_tests, 'cli', 'fixtures')


@pytest.fixture
def run_cli_command():
    """Run a `click` command with the given options.

    The call will raise if the command triggered an exception or the exit code returned is non-zero.
    """

    def _run_cli_command(command, options=None, raises=None):
        """Run the command and check the result.

        :param command: the command to invoke
        :param options: the list of command line options to pass to the command invocation
        :param raises: optionally an exception class that is expected to be raised
        """
        import traceback

        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(command, options or [])

        if raises is not None:
            assert result.exception is not None, result.output
            assert result.exit_code != 0
        else:
            assert result.exception is None, ''.join(traceback.format_exception(*result.exc_info))
            assert result.exit_code == 0, result.output

        result.output_lines = [line.strip() for line in result.output.split('\n') if line.strip()]

        return result

    return _run_cli_command


@pytest.fixture
def launched_processes():
    """Return the list into which ``run_cli_process_launch_command`` records the launched process instances."""
    return []


@pytest.fixture
def run_cli_process_launch_command(run_cli_command, launched_processes, monkeypatch):
    """Run a process launch command with the given options.

    Instead of mocking :meth:`~aiida_hubbard.cli.utils.launch.launch_process` into a no-op, the actual engine launch
    functions are monkeypatched. This way the inputs that the command constructs are still fully validated against the
    process specification -- exactly as they would be upon a real submission -- without any calculation being run. The
    instantiated processes are recorded in the ``launched_processes`` fixture such that tests can assert on the inputs.

    The call will raise if the command triggered an exception or the exit code returned is non-zero.

    :param command: the command to invoke
    :param options: the list of command line options to pass to the command invocation
    :param raises: optionally an exception class that is expected to be raised
    """

    def _instantiate(process, **inputs):
        """Instantiate the process, validating the inputs, and record it in ``launched_processes``."""
        from aiida.engine.utils import instantiate_process
        from aiida.manage import get_manager

        instance = instantiate_process(get_manager().get_runner(), process, **inputs)
        launched_processes.append(instance)
        return instance

    def _mock_submit(process, **inputs):
        """Mock of :meth:`aiida.engine.launch.submit` that validates the inputs instead of submitting."""
        return _instantiate(process, **inputs).node

    def _mock_run_get_node(process, **inputs):
        """Mock of :meth:`aiida.engine.launch.run_get_node` that validates the inputs instead of running."""
        node = _instantiate(process, **inputs).node

        if inputs.get('metadata', {}).get('dry_run', False):
            # Emulate what the engine sets on the node for an actual dry run of a ``CalcJob``.
            node.dry_run_info = {'folder': '.', 'script_filename': '_aiidasubmit.sh'}

        return {}, node

    def _inner(command, options=None, raises=None):
        """Run the command and check the result."""
        from aiida.engine import launch

        monkeypatch.setattr(launch, 'submit', _mock_submit)
        monkeypatch.setattr(launch, 'run_get_node', _mock_run_get_node)
        return run_cli_command(command, options, raises)

    return _inner


@pytest.fixture
def generate_parent_scf_folder(generate_calc_job_node, generate_inputs_pw, generate_hubbard_structure):
    """Return a ``RemoteData`` that is a valid ``parent_scf`` input for an ``HpCalculation``."""

    def _generate_parent_scf_folder(hubbard_structure=None):
        """Return a ``RemoteData`` that is a valid ``parent_scf`` input for an ``HpCalculation``."""
        inputs = generate_inputs_pw(structure=hubbard_structure or generate_hubbard_structure())
        return generate_calc_job_node('quantumespresso.pw', inputs=inputs).outputs.remote_folder

    return _generate_parent_scf_folder
