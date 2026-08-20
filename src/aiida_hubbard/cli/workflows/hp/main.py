"""Command line scripts to launch a `HpWorkChain` for testing and demonstration purposes."""

from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators
import yaml

from ...utils import get_options, launch, options, validate_parallelization
from .. import cmd_launch


@cmd_launch.command('hp-main')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.hp'))
@options.PARENT_FOLDER()
@options.HUBBARD_STRUCTURE()
@options.PROTOCOL()
@options.OVERRIDES()
@options.QPOINTS_MESH()
@options.QPOINTS_DISTANCE()
@options.PARALLELIZE_ATOMS()
@options.PARALLELIZE_QPOINTS()
@options.MAX_NUM_MACHINES()
@options.MAX_WALLCLOCK_SECONDS()
@options.WITH_MPI()
@options.CLEAN_WORKDIR()
@options.DAEMON()
@decorators.with_dbenv()
def launch_workflow(
    code,
    parent_folder,
    hubbard_structure,
    protocol,
    overrides,
    qpoints_mesh,
    qpoints_distance,
    parallelize_atoms,
    parallelize_qpoints,
    max_num_machines,
    max_wallclock_seconds,
    with_mpi,
    clean_workdir,
    daemon,
):
    """Run an `HpWorkChain`.

    It computes the Hubbard parameters, optionally parallelizing the linear response calculation over the Hubbard
    atoms and their perturbations (q-points).
    """
    from aiida.plugins import WorkflowFactory

    overrides = (yaml.safe_load(overrides) or {}) if overrides else {}
    parallelize_atoms, parallelize_qpoints = validate_parallelization(parallelize_atoms, parallelize_qpoints)

    if qpoints_distance is not None:
        overrides['qpoints_distance'] = qpoints_distance

    if parallelize_atoms is not None:
        overrides['parallelize_atoms'] = parallelize_atoms

    if parallelize_qpoints is not None:
        overrides['parallelize_qpoints'] = parallelize_qpoints

    if clean_workdir is not None:
        overrides['clean_workdir'] = clean_workdir

    if hubbard_structure:
        overrides.setdefault('hp', {})['hubbard_structure'] = hubbard_structure

    builder = WorkflowFactory('quantumespresso.hp.main').get_builder_from_protocol(
        code=code,
        protocol=protocol,
        parent_scf_folder=parent_folder,
        overrides=overrides or None,
        options=get_options(max_num_machines, max_wallclock_seconds, with_mpi),
    )

    if qpoints_mesh:
        builder.pop('qpoints_distance', None)
        builder.qpoints = qpoints_mesh

    launch.launch_process(builder, daemon)
