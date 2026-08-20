"""Tests for the ``calculation launch hp`` command."""

from aiida_hubbard.cli.calculations.hp import launch_calculation


def test_command_hp(run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes):
    """Test invoking the calculation launch command with only required inputs."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk)]
    run_cli_process_launch_command(launch_calculation, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.code.uuid == code.uuid
    assert inputs.parent_scf.uuid == parent_scf.uuid
    assert inputs.qpoints.get_kpoints_mesh() == ([1, 1, 1], [0.0, 0.0, 0.0])
    assert inputs.parameters.get_dict() == {'INPUTHP': {}}


def test_command_hp_qpoints_mesh(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the calculation launch command with an explicit q-points mesh."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-q', '2', '2', '2']
    run_cli_process_launch_command(launch_calculation, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.qpoints.get_kpoints_mesh() == ([2, 2, 2], [0.0, 0.0, 0.0])


def test_command_hp_hubbard_structure(
    run_cli_process_launch_command,
    fixture_code,
    generate_hubbard_structure,
    generate_parent_scf_folder,
    launched_processes,
):
    """Test invoking the calculation launch command with an explicit ``HubbardStructureData``."""
    code = fixture_code('quantumespresso.hp').store()
    hubbard_structure = generate_hubbard_structure().store()
    parent_scf = generate_parent_scf_folder(hubbard_structure=hubbard_structure)

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-S', str(hubbard_structure.pk)]
    run_cli_process_launch_command(launch_calculation, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hubbard_structure.uuid == hubbard_structure.uuid


def test_command_hp_options(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the calculation launch command with the computational resource options."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-m', '2', '-w', '3600', '--with-mpi']
    run_cli_process_launch_command(launch_calculation, options=options)

    metadata_options = launched_processes[0].node.get_options()
    assert metadata_options['resources']['num_machines'] == 2
    assert metadata_options['max_wallclock_seconds'] == 3600
    assert metadata_options['withmpi'] is True


def test_command_hp_dry_run(
    run_cli_process_launch_command, fixture_code, generate_parent_scf_folder, launched_processes
):
    """Test invoking the calculation launch command with the ``--dry-run`` option."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--dry-run']
    run_cli_process_launch_command(launch_calculation, options=options)

    assert launched_processes[0].metadata.dry_run is True


def test_command_hp_dry_run_creates_input_file(
    run_cli_command, fixture_code, generate_parent_scf_folder, tmp_path, monkeypatch
):
    """Test that an actual dry run, i.e. without mocking the engine, writes the ``hp.x`` input file."""
    monkeypatch.chdir(tmp_path)
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '-q', '2', '2', '2', '--dry-run']
    result = run_cli_command(launch_calculation, options=options)

    assert 'Running a dry run for HpCalculation' in result.output

    filepaths_input = list(tmp_path.glob('submit_test/*/aiida.in'))
    assert len(filepaths_input) == 1

    content = filepaths_input[0].read_text()
    assert '&INPUTHP' in content
    assert 'nq1' in content


def test_command_hp_dry_run_daemon(run_cli_command, fixture_code, generate_parent_scf_folder):
    """Test that the ``--dry-run`` and ``--daemon`` options are mutually exclusive."""
    code = fixture_code('quantumespresso.hp').store()
    parent_scf = generate_parent_scf_folder()

    options = ['-X', code.full_label, '-P', str(parent_scf.pk), '--dry-run', '--daemon']
    result = run_cli_command(launch_calculation, options=options, raises=True)
    assert 'daemon' in result.output


def test_command_hp_parent_folder_required(run_cli_command, fixture_code):
    """Test that the ``--parent-folder`` option is required."""
    code = fixture_code('quantumespresso.hp').store()

    options = ['-X', code.full_label]
    result = run_cli_command(launch_calculation, options=options, raises=True)
    assert '--parent-folder' in result.output
