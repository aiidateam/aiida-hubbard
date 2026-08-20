"""Pre-defined overridable options for commonly used command line interface parameters."""

from aiida.cmdline.params import types
from aiida.cmdline.params.options import OverridableOption
from aiida.cmdline.utils import decorators
from aiida.common import exceptions
from aiida_quantumespresso.common.types import ElectronicType, RelaxType, SpinType
import click

from . import validate

#: The protocols that are implemented by all the work chains that are exposed through this CLI.
PROTOCOLS = ('fast', 'balanced', 'stringent')

#: The default protocol of all the work chains that are exposed through this CLI.
DEFAULT_PROTOCOL = 'balanced'


class PseudoFamilyType(types.GroupParamType):
    """Subclass of `GroupParamType` in order to be able to print warning with instructions."""

    def __init__(self, pseudo_types=None, **kwargs):
        """Construct a new instance."""
        super().__init__(**kwargs)
        self._pseudo_types = pseudo_types

    @decorators.with_dbenv()
    def convert(self, value, param, ctx):
        """Convert the value to actual pseudo family instance."""
        try:
            group = super().convert(value, param, ctx)
        except click.BadParameter:
            try:
                from aiida.orm import load_group

                load_group(value)
            except exceptions.NotExistent:
                raise

            raise click.BadParameter(
                f'`{value}` is not of a supported pseudopotential family type.\nTo install a supported '
                'pseudofamily, use the `aiida-pseudo` plugin. See the following link for detailed instructions:\n\n'
                '    https://github.com/aiidateam/aiida-quantumespresso#pseudopotentials'
            )

        if self._pseudo_types is not None and group.pseudo_type not in self._pseudo_types:
            pseudo_types = ', '.join(self._pseudo_types)
            raise click.BadParameter(
                f'family `{group.label}` contains pseudopotentials of the wrong type `{group.pseudo_type}`.\nOnly the '
                f'following types are supported: {pseudo_types}'
            )

        return group


class EnumParamType(click.Choice):
    """Subclass of ``click.Choice`` that converts the value into the corresponding member of an ``enum.Enum``."""

    def __init__(self, enum, exclude=(), **kwargs):
        """Construct a new instance.

        :param enum: the enumeration whose members define the valid choices.
        :param exclude: values of the enumeration that should not be exposed as valid choices.
        """
        self._enum = enum
        super().__init__([member.value for member in enum if member.value not in exclude], **kwargs)

    def convert(self, value, param, ctx):
        """Convert the value into the corresponding member of the enumeration."""
        if isinstance(value, self._enum):
            return value

        return self._enum(super().convert(value, param, ctx))


PW_CODE = OverridableOption(
    '--pw',
    'pw_code',
    type=types.CodeParamType(entry_point='quantumespresso.pw'),
    required=True,
    help='The code to use for the pw.x executable.',
)

HP_CODE = OverridableOption(
    '--hp',
    'hp_code',
    type=types.CodeParamType(entry_point='quantumespresso.hp'),
    required=True,
    help='The code to use for the hp.x executable.',
)

HUBBARD_STRUCTURE = OverridableOption(
    '-S',
    '--hubbard-structure',
    type=types.DataParamType(sub_classes=('aiida.data:quantumespresso.hubbard_structure',)),
    help='A HubbardStructureData node identified by its ID or UUID, with initialized Hubbard parameters.',
)

PSEUDO_FAMILY = OverridableOption(
    '-F',
    '--pseudo-family',
    type=PseudoFamilyType(sub_classes=('aiida.groups:pseudo.family',), pseudo_types=('pseudo.upf',)),
    required=False,
    help='Select a pseudopotential family, identified by its label.',
)

PROTOCOL = OverridableOption(
    '-p',
    '--protocol',
    type=click.Choice(PROTOCOLS),
    default=DEFAULT_PROTOCOL,
    show_default=True,
    help='Select the protocol that defines the accuracy of the calculation.',
)

OVERRIDES = OverridableOption(
    '-o',
    '--overrides',
    type=click.File('r'),
    required=False,
    help='The filename or filepath containing the overrides for the protocol, in YAML format.',
)

PARENT_FOLDER = OverridableOption(
    '-P',
    '--parent-folder',
    'parent_folder',
    type=types.DataParamType(sub_classes=('aiida.data:core.remote',)),
    required=True,
    help='The remote folder of the parent pw.x SCF calculation, identified by its ID or UUID.',
)

KPOINTS_MESH = OverridableOption(
    '-k',
    '--kpoints-mesh',
    'kpoints_mesh',
    nargs=3,
    type=click.INT,
    callback=validate.validate_kpoints_mesh,
    help='The number of points in the k-point mesh along each basis vector, e.g. `-k 2 2 2`. If not specified, the '
    'k-points distance defined by the protocol is used instead.',
)

QPOINTS_MESH = OverridableOption(
    '-q',
    '--qpoints-mesh',
    'qpoints_mesh',
    nargs=3,
    type=click.INT,
    callback=validate.validate_kpoints_mesh,
    help='The number of points in the q-point mesh along each basis vector, e.g. `-q 2 2 2`.',
)

QPOINTS_DISTANCE = OverridableOption(
    '-Q',
    '--qpoints-distance',
    type=click.FLOAT,
    required=False,
    help='The minimum desired distance in 1/Å between q-points in reciprocal space.',
)

MAX_NUM_MACHINES = OverridableOption(
    '-m',
    '--max-num-machines',
    type=click.INT,
    required=False,
    help='The maximum number of machines (nodes) to use for the calculations.',
)

MAX_WALLCLOCK_SECONDS = OverridableOption(
    '-w',
    '--max-wallclock-seconds',
    type=click.INT,
    required=False,
    help='The maximum wallclock time in seconds to set for the calculations.',
)

WITH_MPI = OverridableOption(
    '-i',
    '--with-mpi/--without-mpi',
    'with_mpi',
    default=None,
    help='Run the calculations with MPI enabled.',
)

DAEMON = OverridableOption(
    '--daemon/--no-daemon',
    '-D',
    'daemon',
    default=True,
    show_default=True,
    help='Submit the process to the daemon instead of running it and waiting for it to finish.',
)

CLEAN_WORKDIR = OverridableOption(
    '-x',
    '--clean-workdir/--no-clean-workdir',
    'clean_workdir',
    default=None,
    help='Clean the remote folders of all the launched calculations after completion of the work chain. If not '
    'specified, the value defined by the protocol is used.',
)

ELECTRONIC_TYPE = OverridableOption(
    '--electronic-type',
    type=EnumParamType(ElectronicType, exclude=('automatic',)),
    default=ElectronicType.METAL.value,
    show_default=True,
    help='Select the electronic type of the system.',
)

SPIN_TYPE = OverridableOption(
    '--spin-type',
    type=EnumParamType(SpinType, exclude=('non_collinear', 'spin_orbit')),
    default=SpinType.NONE.value,
    show_default=True,
    help='Select the spin polarization type of the system.',
)

RELAX_TYPE = OverridableOption(
    '--relax-type',
    type=EnumParamType(RelaxType, exclude=('volume', 'positions_volume')),
    default=RelaxType.POSITIONS_CELL.value,
    show_default=True,
    help='Select what should be optimized by the geometry optimization steps.',
)

ONLY_INITIALIZATION = OverridableOption(
    '--only-initialization',
    is_flag=True,
    default=False,
    show_default=True,
    help='Only run the initialization step of the hp.x calculation, which determines the number of perturbations.',
)

PARALLELIZE_ATOMS = OverridableOption(
    '--parallelize-atoms/--no-parallelize-atoms',
    'parallelize_atoms',
    default=None,
    help='Parallelize the linear response calculation over the Hubbard atoms. If not specified, the value defined by '
    'the protocol is used.',
)

PARALLELIZE_QPOINTS = OverridableOption(
    '--parallelize-qpoints/--no-parallelize-qpoints',
    'parallelize_qpoints',
    default=None,
    help='Parallelize the linear response calculation over the q-points. This requires the parallelization over the '
    'Hubbard atoms to be enabled. If not specified, the value defined by the protocol is used.',
)
