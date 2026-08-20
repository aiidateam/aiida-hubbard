"""Tests for the ``workflow launch hp-main`` command."""

from pathlib import Path

from aiida_hubbard.cli.workflows.hp.main import launch_workflow


def test_command_hp_main(run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes):
    """Test invoking the workflow launch command with only required inputs."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk)]
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hp.code.uuid == code.uuid
    assert inputs.hp.parent_scf.uuid == parent_scf.uuid
    # These are the values of the default ``balanced`` protocol of the ``HpWorkChain``.
    assert inputs.qpoints_distance.value == 0.8
    assert inputs.parallelize_atoms.value is True
    assert inputs.parallelize_qpoints.value is True
    assert inputs.clean_workdir.value is True
    # The ``qpoints`` of the ``HpBaseWorkChain`` namespace are excluded by the ``HpWorkChain``.
    assert 'qpoints' not in inputs.hp


def test_command_hp_main_protocol(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the ``--protocol`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-p', 'fast']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.qpoints_distance.value == 1.2
    assert inputs.hp.parameters['INPUTHP']['conv_thr_chi'] == 1e-4


def test_command_hp_main_overrides(
    run_cli_process_launch_command,
    fixture_code,
    generate_parent_scf_folder,
    filepath_cli_fixtures,
    launched_processes,
):
    """Test invoking the workflow launch command with the ``--overrides`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()
    filepath_overrides = Path(filepath_cli_fixtures, 'overrides', 'hp-main.yaml')

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-o', str(filepath_overrides)]
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.qpoints_distance.value == 1.5
    assert inputs.hp.parameters['INPUTHP']['conv_thr_chi'] == 1e-3


def test_command_hp_main_qpoints_mesh(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with an explicit q-points mesh."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-q', '4', '4', '4']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.qpoints.get_kpoints_mesh() == ([4, 4, 4], [0.0, 0.0, 0.0])
    assert 'qpoints_distance' not in inputs


def test_command_hp_main_qpoints_distance(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with an explicit q-points distance."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-Q', '0.4']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.qpoints_distance.value == 0.4
    assert 'qpoints' not in inputs


def test_command_hp_main_parallelization(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the workflow launch command with the parallelization options."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = [
        '-X',
        code.full_label,
        '-P',
        str(parent_scf.pk),
        '--no-parallelize-atoms',
        '--no-parallelize-qpoints',
    ]
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.parallelize_atoms.value is False
    assert inputs.parallelize_qpoints.value is False


def test_command_hp_main_parallelization_implied(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test that disabling the atom parallelization implies disabling the q-point parallelization."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--no-parallelize-atoms']
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.parallelize_atoms.value is False
    assert inputs.parallelize_qpoints.value is False


def test_command_hp_main_parallelization_invalid(run_cli_command, fixture_code, generate_parent_scf_folder):
    """Test that q-point parallelization cannot be requested without atom parallelization."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--no-parallelize-atoms', '--parallelize-qpoints']
    result = run_cli_command(launch_workflow, options=options, raises=True)
    assert '--parallelize-qpoints' in result.output


def test_command_hp_main_hubbard_structure(
    run_cli_process_launch_command,
    fixture_code,
    generate_hubbard_structure,
    generate_parent_scf_folder,
    launched_processes,
):
    """Test invoking the workflow launch command with an explicit ``HubbardStructureData``."""
    code = fixture_code('quantumespresso.hp').store()
    hubbard_structure = generate_hubbard_structure().store()
    parent_scf = generate_parent_scf_folder(hubbard_structure=hubbard_structure)

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-S', str(hubbard_structure.pk)]
    run_cli_process_launch_command(launch_workflow, options=options)

    assert launched_processes[0].inputs.hp.hubbard_structure.uuid == hubbard_structure.uuid


def test_command_hp_main_options(
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
