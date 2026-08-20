"""Tests for the ``workflow launch hp-base`` command."""

from pathlib import Path

from aiida_hubbard.cli.workflows.hp.base import launch_workflow


def test_command_hp_base(run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes):
    """Test invoking the workflow launch command with only required inputs."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk)]
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hp.code.uuid == code.uuid
    assert inputs.hp.parent_scf.uuid == parent_scf.uuid
    # These are the values of the default ``balanced`` protocol of the ``HpBaseWorkChain``.
    assert inputs.hp.qpoints.get_kpoints_mesh() == ([2, 2, 2], [0.0, 0.0, 0.0])
    assert inputs.hp.parameters['INPUTHP']['conv_thr_chi'] == 5e-6
    assert inputs.clean_workdir.value is True
    assert inputs.only_initialization.value is False


def test_command_hp_base_protocol(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the ``--protocol`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-p', 'fast']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hp.qpoints.get_kpoints_mesh() == ([1, 1, 1], [0.0, 0.0, 0.0])
    assert inputs.hp.parameters['INPUTHP']['conv_thr_chi'] == 1e-4


def test_command_hp_base_overrides(
    run_cli_process_launch_command,
    fixture_code,
    generate_parent_scf_folder,
    filepath_cli_fixtures,
    launched_processes,
):
    """Test invoking the workflow launch command with the ``--overrides`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()
    filepath_overrides = Path(filepath_cli_fixtures, 'overrides', 'hp-base.yaml')

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-o', str(filepath_overrides)]
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hp.parameters['INPUTHP']['conv_thr_chi'] == 1e-3
    assert inputs.clean_workdir.value is False


def test_command_hp_base_qpoints_mesh(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with an explicit q-points mesh."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-q', '4', '4', '4']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hp.qpoints.get_kpoints_mesh() == ([4, 4, 4], [0.0, 0.0, 0.0])


def test_command_hp_base_only_initialization(
    run_cli_process_launch_command,
    fixture_code,
    generate_hubbard_structure,
    generate_parent_scf_folder,
    launched_processes,
):
    """Test invoking the workflow launch command with the ``--only-initialization`` option."""
    code = fixture_code('quantumespresso.hp').store()
    hubbard_structure = generate_hubbard_structure().store()
    parent_scf = generate_parent_scf_folder(hubbard_structure=hubbard_structure)

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-S', str(hubbard_structure.pk)]
    options.append('--only-initialization')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.only_initialization.value is True
    assert inputs.hp.hubbard_structure.uuid == hubbard_structure.uuid


def test_command_hp_base_only_initialization_no_structure(run_cli_command, fixture_code, generate_parent_scf_folder):
    """Test that ``--only-initialization`` requires an explicit ``HubbardStructureData``."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--only-initialization']
    result = run_cli_command(launch_workflow, options=options, raises=True)
    assert '--hubbard-structure' in result.output


def test_command_hp_base_options(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the computational resource options."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-m', '3', '-w', '600', '--without-mpi']
    run_cli_process_launch_command(launch_workflow, options=options)

    metadata_options = launched_processes[0].inputs.hp.metadata['options']
    assert metadata_options['resources']['num_machines'] == 3
    assert metadata_options['max_wallclock_seconds'] == 600
    assert metadata_options['withmpi'] is False


def test_command_hp_base_no_daemon(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the ``--no-daemon`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--no-daemon']
    result = run_cli_process_launch_command(launch_workflow, options=options)

    assert 'Running a HpBaseWorkChain' in result.output
    assert f'HpBaseWorkChain<{launched_processes[0].node.pk}>' in result.output


def test_command_hp_base_clean_workdir(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the ``--no-clean-workdir`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--no-clean-workdir']
    run_cli_process_launch_command(launch_workflow, options=options)

    assert launched_processes[0].inputs.clean_workdir.value is False
