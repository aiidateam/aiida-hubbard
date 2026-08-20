"""Utilities for the command line interface."""

import click


def validate_parallelization(parallelize_atoms, parallelize_qpoints):
    """Validate the parallelization options of the ``HpWorkChain``.

    Parallelization over the perturbations (q-points) is only possible if the calculation is also parallelized over
    the Hubbard atoms. Explicitly requesting the former while disabling the latter is therefore an error, whereas
    disabling the latter without specifying the former simply implies that the former is disabled as well.

    :param parallelize_atoms: whether to parallelize over the Hubbard atoms, or ``None`` if not specified.
    :param parallelize_qpoints: whether to parallelize over the q-points, or ``None`` if not specified.
    :return: tuple of the validated ``parallelize_atoms`` and ``parallelize_qpoints`` values.
    :raises click.BadParameter: if q-point parallelization is requested without atom parallelization.
    """
    if parallelize_atoms is False:
        if parallelize_qpoints:
            raise click.BadParameter(
                'q-point parallelization is only possible when parallelizing over the Hubbard atoms',
                param_hint='--parallelize-qpoints',
            )
        parallelize_qpoints = False

    return parallelize_atoms, parallelize_qpoints


def get_options(max_num_machines=None, max_wallclock_seconds=None, with_mpi=None):
    """Return a ``metadata.options`` dictionary containing only the options that were explicitly specified.

    The returned dictionary is intended to be passed to the ``options`` keyword of a ``get_builder_from_protocol``
    method, where it is recursively merged with the options defined by the protocol. Returning ``None`` when nothing
    was specified therefore guarantees that the protocol defaults are left untouched.

    :param max_num_machines: the maximum number of machines (nodes) to use for the calculations.
    :param max_wallclock_seconds: the maximum wallclock time in seconds to set for the calculations.
    :param with_mpi: whether to run the calculations with MPI enabled.
    :return: dictionary of ``metadata.options`` or ``None`` if no option was specified.
    """
    options = {}

    if max_num_machines is not None:
        options['resources'] = {'num_machines': max_num_machines}

    if max_wallclock_seconds is not None:
        options['max_wallclock_seconds'] = max_wallclock_seconds

    if with_mpi is not None:
        options['withmpi'] = with_mpi

    return options or None
