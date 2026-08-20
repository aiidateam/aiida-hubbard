"""Tests for the ``workflow launch hubbard`` command."""

from pathlib import Path

import pytest

from aiida_hubbard.cli.workflows.hubbard import launch_workflow


@pytest.fixture
def generate_options(fixture_code, generate_hubbard_structure):
    """Return the minimally required command line options for the ``hubbard`` launch command."""

    def _generate_options(*args):
        pw_code = fixture_code('quantumespresso.pw').store()
        hp_code = fixture_code('quantumespresso.hp').store()
        hubbard_structure = generate_hubbard_structure().store()

        options = [
            '--pw',
            pw_code.full_label,
            '--hp',
            hp_code.full_label,
            '-S',
            str(hubbard_structure.pk),
            '-p',
            'fast',
        ]
        options.extend(args)

        return options

    return _generate_options


def test_command_hubbard(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with only required inputs."""
    options = generate_options()
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs

    # The stale inputs of the legacy CLI should no longer be part of the constructed inputs.
    for key in ('structure', 'hubbard_u', 'recon'):
        assert key not in inputs

    # The ``relax`` namespace of the ``PwRelaxWorkChain`` in ``aiida-quantumespresso~=5.0``.
    assert 'base_relax' in inputs.relax
    assert 'base_init_relax' in inputs.relax
    assert 'base' not in inputs.relax
    assert 'base_final_scf' not in inputs.relax

    assert 'hubbard_structure' in inputs
    assert 'pw' in inputs.scf
    assert 'hp' in inputs.hubbard

    # These are the values of the ``fast`` protocol of the ``SelfConsistentHubbardWorkChain``.
    assert inputs.tolerance_onsite.value == 0.2
    assert inputs.tolerance_intersite.value == 0.1
    assert inputs.scf.kpoints_distance.value == 0.6
    assert inputs.meta_convergence.value is True
    assert inputs.clean_workdir.value is True


def test_command_hubbard_codes(run_cli_process_launch_command, generate_options, launched_processes):
    """Test that the ``--pw`` and ``--hp`` codes end up in the correct namespaces."""
    options = generate_options()
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    pw_code_label = options[1]
    hp_code_label = options[3]

    assert inputs.scf.pw.code.full_label == pw_code_label
    assert inputs.relax.base_relax.pw.code.full_label == pw_code_label
    assert inputs.relax.base_init_relax.pw.code.full_label == pw_code_label
    assert inputs.hubbard.hp.code.full_label == hp_code_label


def test_command_hubbard_default_structure(run_cli_process_launch_command, fixture_code, launched_processes):
    """Test invoking the workflow launch command without an explicit structure."""
    from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData

    pw_code = fixture_code('quantumespresso.pw').store()
    hp_code = fixture_code('quantumespresso.hp').store()

    options = ['--pw', pw_code.full_label, '--hp', hp_code.full_label, '-p', 'fast']
    run_cli_process_launch_command(launch_workflow, options=options)

    hubbard_structure = launched_processes[0].inputs.hubbard_structure
    assert isinstance(hubbard_structure, HubbardStructureData)
    assert len(hubbard_structure.hubbard.parameters) > 0


def test_command_hubbard_no_relax(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--no-relax`` option."""
    options = generate_options('--no-relax')
    run_cli_process_launch_command(launch_workflow, options=options)

    assert 'relax' not in launched_processes[0].inputs


def test_command_hubbard_no_init_relax(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--no-init-relax`` option."""
    options = generate_options('--no-init-relax')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert 'base_relax' in inputs.relax
    assert 'base_init_relax' not in inputs.relax


def test_command_hubbard_kpoints_mesh(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with an explicit k-points mesh."""
    options = generate_options('-k', '2', '2', '2')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    mesh = ([2, 2, 2], [0.0, 0.0, 0.0])

    assert 'kpoints_distance' not in inputs.scf
    assert inputs.scf.kpoints.get_kpoints_mesh() == mesh
    assert inputs.relax.base_relax.kpoints.get_kpoints_mesh() == mesh
    assert inputs.relax.base_init_relax.kpoints.get_kpoints_mesh() == mesh


def test_command_hubbard_kpoints_mesh_no_relax(run_cli_process_launch_command, generate_options, launched_processes):
    """Test that an explicit k-points mesh can be combined with the ``--no-relax`` option."""
    options = generate_options('--no-relax', '-k', '2', '2', '2')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert 'relax' not in inputs
    assert inputs.scf.kpoints.get_kpoints_mesh() == ([2, 2, 2], [0.0, 0.0, 0.0])


def test_command_hubbard_qpoints_mesh(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with an explicit q-points mesh."""
    options = generate_options('-q', '3', '3', '3')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs

    assert 'qpoints_distance' not in inputs.hubbard
    assert inputs.hubbard.qpoints.get_kpoints_mesh() == ([3, 3, 3], [0.0, 0.0, 0.0])


def test_command_hubbard_pseudo_family(run_cli_process_launch_command, generate_options, launched_processes, sssp):
    """Test invoking the workflow launch command with the ``--pseudo-family`` option."""
    options = generate_options('-F', sssp.label)
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    pseudos = inputs.scf.pw.pseudos

    assert sorted(pseudos.keys()) == ['Co', 'Li', 'O']
    assert all(pseudo.uuid in [node.uuid for node in sssp.nodes] for pseudo in pseudos.values())


def test_command_hubbard_overrides(
    run_cli_process_launch_command, generate_options, filepath_cli_fixtures, launched_processes
):
    """Test invoking the workflow launch command with the ``--overrides`` option."""
    filepath_overrides = Path(filepath_cli_fixtures, 'overrides', 'hubbard.yaml')
    options = generate_options('-o', str(filepath_overrides))
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.tolerance_onsite.value == 0.5
    assert inputs.max_iterations.value == 3
    assert inputs.scf.kpoints_distance.value == 1.0


def test_command_hubbard_electronic_type(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--electronic-type`` option."""
    options = generate_options('--electronic-type', 'insulator')
    run_cli_process_launch_command(launch_workflow, options=options)

    parameters = launched_processes[0].inputs.scf.pw.parameters.get_dict()
    assert parameters['SYSTEM']['occupations'] == 'fixed'
    assert 'smearing' not in parameters['SYSTEM']


def test_command_hubbard_spin_type(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--spin-type`` option."""
    options = generate_options('--spin-type', 'collinear')
    run_cli_process_launch_command(launch_workflow, options=options)

    parameters = launched_processes[0].inputs.scf.pw.parameters.get_dict()
    assert parameters['SYSTEM']['nspin'] == 2
    assert 'starting_magnetization' in parameters['SYSTEM']


def test_command_hubbard_relax_type(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--relax-type`` option."""
    options = generate_options('--relax-type', 'positions')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.relax.base_relax.pw.parameters['CONTROL']['calculation'] == 'relax'
    assert 'CELL' not in inputs.relax.base_relax.pw.parameters.get_dict()


def test_command_hubbard_meta_convergence(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--no-meta-convergence`` option."""
    options = generate_options('--no-meta-convergence')
    run_cli_process_launch_command(launch_workflow, options=options)

    assert launched_processes[0].inputs.meta_convergence.value is False


def test_command_hubbard_clean_workdir(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the ``--no-clean-workdir`` option."""
    options = generate_options('--no-clean-workdir')
    run_cli_process_launch_command(launch_workflow, options=options)

    assert launched_processes[0].inputs.clean_workdir.value is False


def test_command_hubbard_parallelization(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the parallelization options."""
    options = generate_options('--no-parallelize-atoms', '--no-parallelize-qpoints')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hubbard.parallelize_atoms.value is False
    assert inputs.hubbard.parallelize_qpoints.value is False


def test_command_hubbard_parallelization_implied(run_cli_process_launch_command, generate_options, launched_processes):
    """Test that disabling the atom parallelization implies disabling the q-point parallelization."""
    options = generate_options('--no-parallelize-atoms')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs
    assert inputs.hubbard.parallelize_atoms.value is False
    assert inputs.hubbard.parallelize_qpoints.value is False


def test_command_hubbard_parallelization_invalid(run_cli_command, generate_options):
    """Test that q-point parallelization cannot be requested without atom parallelization."""
    options = generate_options('--no-parallelize-atoms', '--parallelize-qpoints')

    result = run_cli_command(launch_workflow, options=options, raises=True)
    assert '--parallelize-qpoints' in result.output


def test_command_hubbard_options(run_cli_process_launch_command, generate_options, launched_processes):
    """Test invoking the workflow launch command with the computational resource options."""
    options = generate_options('-m', '4', '-w', '900', '--without-mpi')
    run_cli_process_launch_command(launch_workflow, options=options)

    inputs = launched_processes[0].inputs

    for metadata in (
        inputs.scf.pw.metadata,
        inputs.relax.base_relax.pw.metadata,
        inputs.relax.base_init_relax.pw.metadata,
        inputs.hubbard.hp.metadata,
    ):
        assert metadata['options']['resources']['num_machines'] == 4
        assert metadata['options']['max_wallclock_seconds'] == 900
        assert metadata['options']['withmpi'] is False


def test_command_hubbard_invalid_protocol(run_cli_command, generate_options):
    """Test invoking the workflow launch command with an invalid protocol."""
    options = generate_options()
    options[options.index('-p') + 1] = 'not-a-protocol'

    result = run_cli_command(launch_workflow, options=options, raises=True)
    assert 'not-a-protocol' in result.output
