"""Command line scripts to launch a `HpCalculation` for testing and demonstration purposes."""

from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators
import click
from click.core import ParameterSource

from ..utils import launch, options
from . import cmd_launch


@cmd_launch.command('hp')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.hp'))
@options.PARENT_FOLDER()
@options.HUBBARD_STRUCTURE()
@options.QPOINTS_MESH(default=(1, 1, 1), show_default=True)
@options.MAX_NUM_MACHINES(default=1, show_default=True)
@options.MAX_WALLCLOCK_SECONDS(default=1800, show_default=True)
@options.WITH_MPI(default=False, show_default=True)
@options.DAEMON()
@options_core.DRY_RUN()
@click.pass_context
@decorators.with_dbenv()
def launch_calculation(
    ctx,
    code,
    parent_folder,
    hubbard_structure,
    qpoints_mesh,
    max_num_machines,
    max_wallclock_seconds,
    with_mpi,
    daemon,
    dry_run,
):
    """Run an `HpCalculation`."""
    from aiida import orm
    from aiida.plugins import CalculationFactory
    from aiida_quantumespresso.utils.resources import get_default_options

    inputs = {
        'code': code,
        'qpoints': qpoints_mesh,
        'parameters': orm.Dict({'INPUTHP': {}}),
        'parent_scf': parent_folder,
        'metadata': {
            'options': get_default_options(max_num_machines, max_wallclock_seconds, with_mpi),
        },
    }

    if hubbard_structure:
        inputs['hubbard_structure'] = hubbard_structure

    if dry_run:
        if daemon and ctx.get_parameter_source('daemon') is not ParameterSource.DEFAULT:
            raise click.BadParameter('cannot send to the daemon if in dry_run mode', param_hint='--daemon')
        daemon = False
        inputs['metadata']['store_provenance'] = False
        inputs['metadata']['dry_run'] = True

    launch.launch_process(CalculationFactory('quantumespresso.hp'), daemon, **inputs)
