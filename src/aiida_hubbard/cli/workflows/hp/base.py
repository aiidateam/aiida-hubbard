"""Command line scripts to launch a `HpBaseWorkChain` for testing and demonstration purposes."""

from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators
import click
import yaml

from ...utils import get_options, launch, options
from .. import cmd_launch


@cmd_launch.command('hp-base')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.hp'))
@options.PARENT_FOLDER()
@options.HUBBARD_STRUCTURE()
@options.PROTOCOL()
@options.OVERRIDES()
@options.QPOINTS_MESH()
@options.ONLY_INITIALIZATION()
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
    only_initialization,
    max_num_machines,
    max_wallclock_seconds,
    with_mpi,
    clean_workdir,
    daemon,
):
    """Run an `HpBaseWorkChain`."""
    from aiida.plugins import WorkflowFactory

    overrides = (yaml.safe_load(overrides) or {}) if overrides else {}

    if only_initialization:
        if not hubbard_structure:
            raise click.BadParameter(
                'the `hp.x` initialization requires a `HubbardStructureData` to determine the perturbed atoms',
                param_hint='--hubbard-structure',
            )
        overrides['only_initialization'] = True

    if clean_workdir is not None:
        overrides['clean_workdir'] = clean_workdir

    if hubbard_structure:
        overrides.setdefault('hp', {})['hubbard_structure'] = hubbard_structure

    builder = WorkflowFactory('quantumespresso.hp.base').get_builder_from_protocol(
        code=code,
        protocol=protocol,
        parent_scf_folder=parent_folder,
        overrides=overrides or None,
        options=get_options(max_num_machines, max_wallclock_seconds, with_mpi),
    )

    if qpoints_mesh:
        builder.hp.qpoints = qpoints_mesh

    launch.launch_process(builder, daemon)
