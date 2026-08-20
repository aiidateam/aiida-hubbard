"""Command line scripts to launch a `SelfConsistentHubbardWorkChain` for testing and demonstration purposes."""

from aiida.cmdline.utils import decorators
import click
import yaml

from ..utils import defaults, get_options, launch, options, validate_parallelization
from . import cmd_launch


@cmd_launch.command('hubbard')
@options.PW_CODE()
@options.HP_CODE()
@options.HUBBARD_STRUCTURE(
    default=defaults.get_hubbard_structure,
    help='A HubbardStructureData node identified by its ID or UUID, with initialized Hubbard parameters. If not '
    'specified, a bulk LiCoO2 structure with an initialized on-site Hubbard U on cobalt is used.',
)
@options.PROTOCOL()
@options.OVERRIDES()
@options.PSEUDO_FAMILY()
@options.KPOINTS_MESH()
@options.QPOINTS_MESH()
@options.ELECTRONIC_TYPE()
@options.SPIN_TYPE()
@options.RELAX_TYPE()
@click.option(
    '--relax/--no-relax',
    'relax',
    default=True,
    show_default=True,
    help='Iteratively relax the structure with the `PwRelaxWorkChain` during the self-consistent cycle.',
)
@click.option(
    '--init-relax/--no-init-relax',
    'init_relax',
    default=True,
    show_default=True,
    help='Prepend a relaxation with looser thresholds to each relaxation step.',
)
@click.option(
    '--meta-convergence/--no-meta-convergence',
    'meta_convergence',
    default=None,
    help='Run the self-consistent cycle until the Hubbard parameters are converged. If not specified, the value '
    'defined by the protocol is used.',
)
@options.PARALLELIZE_ATOMS()
@options.PARALLELIZE_QPOINTS()
@options.MAX_NUM_MACHINES()
@options.MAX_WALLCLOCK_SECONDS()
@options.WITH_MPI()
@options.CLEAN_WORKDIR()
@options.DAEMON()
@decorators.with_dbenv()
def launch_workflow(
    pw_code,
    hp_code,
    hubbard_structure,
    protocol,
    overrides,
    pseudo_family,
    kpoints_mesh,
    qpoints_mesh,
    electronic_type,
    spin_type,
    relax_type,
    relax,
    init_relax,
    meta_convergence,
    parallelize_atoms,
    parallelize_qpoints,
    max_num_machines,
    max_wallclock_seconds,
    with_mpi,
    clean_workdir,
    daemon,
):
    """Run a `SelfConsistentHubbardWorkChain`.

    It computes the self-consistent Hubbard parameters of the given `HubbardStructureData`, iterating a
    (relax-)scf-hp cycle until the Hubbard parameters are converged within the tolerances of the protocol.
    """
    from aiida.plugins import WorkflowFactory

    overrides = (yaml.safe_load(overrides) or {}) if overrides else {}
    parallelize_atoms, parallelize_qpoints = validate_parallelization(parallelize_atoms, parallelize_qpoints)

    if pseudo_family:
        overrides.setdefault('scf', {})['pseudo_family'] = pseudo_family.label
        relax_overrides = overrides.setdefault('relax', {})
        relax_overrides.setdefault('base_relax', {})['pseudo_family'] = pseudo_family.label
        relax_overrides.setdefault('base_init_relax', {})['pseudo_family'] = pseudo_family.label

    if meta_convergence is not None:
        overrides['meta_convergence'] = meta_convergence

    if clean_workdir is not None:
        overrides['clean_workdir'] = clean_workdir

    if parallelize_atoms is not None:
        overrides.setdefault('hubbard', {})['parallelize_atoms'] = parallelize_atoms

    if parallelize_qpoints is not None:
        overrides.setdefault('hubbard', {})['parallelize_qpoints'] = parallelize_qpoints

    builder = WorkflowFactory('quantumespresso.hp.hubbard').get_builder_from_protocol(
        pw_code=pw_code,
        hp_code=hp_code,
        hubbard_structure=hubbard_structure,
        protocol=protocol,
        overrides=overrides or None,
        options_pw=get_options(max_num_machines, max_wallclock_seconds, with_mpi),
        options_hp=get_options(max_num_machines, max_wallclock_seconds, with_mpi),
        electronic_type=electronic_type,
        spin_type=spin_type,
        relax_type=relax_type,
    )

    if not relax:
        builder.pop('relax', None)
    elif not init_relax:
        builder.relax.pop('base_init_relax', None)

    if kpoints_mesh:
        builder.scf.pop('kpoints_distance', None)
        builder.scf.kpoints = kpoints_mesh

        if 'relax' in builder:
            for namespace in ('base_init_relax', 'base_relax'):
                if namespace in builder.relax:
                    builder.relax[namespace].pop('kpoints_distance', None)
                    builder.relax[namespace].kpoints = kpoints_mesh

    if qpoints_mesh:
        builder.hubbard.pop('qpoints_distance', None)
        builder.hubbard.qpoints = qpoints_mesh

    launch.launch_process(builder, daemon)
