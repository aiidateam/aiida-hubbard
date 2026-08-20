"""Utility functions for validation of command line interface parameter inputs."""

from aiida.cmdline.utils import decorators
import click


@decorators.with_dbenv()
def validate_kpoints_mesh(ctx, param, value):
    """Command line option validator for a kpoints mesh tuple.

    The value should be a tuple of three positive integers out of which a ``KpointsData`` object will be created with a
    mesh equal to the tuple.

    :param ctx: internal context of the click.command
    :param param: the click Parameter, i.e. either the Option or Argument to which the validator is hooked up
    :param value: a tuple of three positive integers
    :returns: a ``KpointsData`` instance
    """
    from aiida.orm import KpointsData

    if not value:
        return None

    if any(not isinstance(integer, int) for integer in value) or any(int(i) <= 0 for i in value):
        raise click.BadParameter('all values of the tuple should be positive greater than zero integers')

    try:
        kpoints = KpointsData()
        kpoints.set_kpoints_mesh(value)
    except ValueError as exception:
        raise click.BadParameter(f'failed to create a KpointsData mesh out of {value}\n{exception}')

    return kpoints
