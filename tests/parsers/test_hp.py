# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,redefined-outer-name
"""Tests for the `HpParser`."""
from aiida import orm
from aiida.common import AttributeDict
import pytest

from aiida_hubbard.calculations.hp import HpCalculation


@pytest.fixture
def generate_inputs_default(generate_hubbard_structure):
    """Return only those inputs that the parser will expect to be there.

    .. note:: default is to have Hubbard U only (no U+V)
    """

    def _generate_inputs_default(only_u=True):
        """Return only those inputs that the parser will expect to be there."""
        parameters = {'INPUTHP': {}}
        return AttributeDict({
            'parameters': orm.Dict(parameters),
            'hubbard_structure': generate_hubbard_structure(only_u=only_u)
        })

    return _generate_inputs_default


@pytest.fixture
def generate_inputs_init_only():
    """Return only those inputs that the parser will expect to be there."""
    parameters = {'INPUTHP': {'determine_num_pert_only': True}}
    return AttributeDict({'parameters': orm.Dict(parameters)})


@pytest.fixture
def generate_inputs_mesh_only():
    """Return only those inputs that the parser will expect to be there."""
    parameters = {'INPUTHP': {'determine_q_mesh_only': True, 'perturb_only_atom(1)': True}}
    return AttributeDict({'parameters': orm.Dict(parameters)})


@pytest.fixture
def generate_inputs_voronoi(filepath_tests):
    """Return inputs that the parser will expect when nearest-neighbours analysis is active."""

    def _generate_inputs_voronoi(all_neihbours=False):
        """Return inputs that the parser will expect when nearest-neighbours analysis is active."""
        import os

        from aiida_quantumespresso.utils.hubbard import initialize_hubbard_parameters
        from ase.io import read
        path = os.path.join(filepath_tests, 'fixtures', 'structures', 'MnCoS.cif')
        atoms = read(path)
        pairs = {
            'Mn': ['3d', 5.0, 1e-8, {
                'S': '3p'
            }],
            'Co': ['3d', 5.0, 1e-8, {
                'S': '3p'
            }],
        }
        if all_neihbours:
            pairs = {
                'Mn': ['3d', 5.0, 1e-8, {
                    'S': '3p',
                    'Co': '3d'
                }],
                'Co': ['3d', 5.0, 1e-8, {
                    'S': '3p',
                    'Mn': '3d'
                }],
            }
        structure = orm.StructureData(ase=atoms)
        hubbard_structure = initialize_hubbard_parameters(structure=structure, pairs=pairs)
        parameters = {'INPUTHP': {'num_neigh': 10}}
        settings = {'radial_analysis': {}}
        return AttributeDict({
            'parameters': orm.Dict(parameters),
            'settings': orm.Dict(settings),
            'hubbard_structure': hubbard_structure,
        })

    return _generate_inputs_voronoi


def test_hp_default(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_default, data_regression, tmpdir
):
    """Test a default `hp.x` calculation."""
    name = 'default'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_default(only_u=True),
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' in results
    assert 'hubbard_chi' in results
    assert 'hubbard_matrices' in results
    assert 'hubbard_structure' in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
        'hubbard_chi': results['hubbard_chi'].base.attributes.all,
        'hubbard_matrices': results['hubbard_matrices'].base.attributes.all,
        'hubbard': results['hubbard'].get_dict(),
        'hubbard_data': results['hubbard_structure'].hubbard.dict(),
    })


def test_hp_default_hubbard_structure(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_default, data_regression, tmpdir
):
    """Test a default `hp.x` calculation."""
    name = 'default_hubbard_structure'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_default(only_u=False),
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' in results
    assert 'hubbard_chi' in results
    assert 'hubbard_structure' in results
    assert 'hubbard_matrices' in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
        'hubbard': results['hubbard'].get_dict(),
        'hubbard_chi': results['hubbard_chi'].base.attributes.all,
        'hubbard_matrices': results['hubbard_matrices'].base.attributes.all,
        'hubbard_data': results['hubbard_structure'].hubbard.dict(),
    })


@pytest.mark.parametrize('all_neihbours', (True, False))
def test_hp_voronoi_hubbard_structure(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_voronoi, data_regression, tmpdir,
    all_neihbours
):
    """Test a `hp.x` calculation with nearest-neihbour analysis."""
    name = 'voronoi_hubbard_structure'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_voronoi(all_neihbours),
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' in results
    assert 'hubbard_chi' in results
    assert 'hubbard_structure' in results
    assert 'hubbard_matrices' in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
        'hubbard': results['hubbard'].get_dict(),
        'hubbard_chi': results['hubbard_chi'].base.attributes.all,
        'hubbard_matrices': results['hubbard_matrices'].base.attributes.all,
        'hubbard_data': results['hubbard_structure'].hubbard.dict(),
    })


def test_hp_initialization_only(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_init_only, data_regression
):
    """Test an initialization only `hp.x` calculation with onsites only."""
    name = 'initialization_only'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_init_only)
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' not in results
    assert 'hubbard_chi' not in results
    assert 'hubbard_matrices' not in results
    assert 'hubbard_structure' not in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
    })


def test_hp_initialization_only_intersites(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_init_only, data_regression, tmpdir
):
    """Test an initialization only `hp.x` calculation with intersites."""
    name = 'initialization_only_intersites'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    # QE generates the ``HUBBARD.dat``, but with empty values, thus we make sure the parser
    # does not recognize it as a final calculation and it does not crash as a consequence.
    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_init_only,
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' not in results
    assert 'hubbard_chi' not in results
    assert 'hubbard_matrices' not in results
    assert 'hubbard_structure' not in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
    })


def test_hp_initialization_only_mesh(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_mesh_only, data_regression, tmpdir
):
    """Test an initialization only `hp.x` calculation with intersites."""
    name = 'initialization_only_mesh'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    # QE generates the ``HUBBARD.dat``, but with empty values, thus we make sure the parser
    # does not recognize it as a final calculation and it does not crash as a consequence.
    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_mesh_only,
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' not in results
    assert 'hubbard_chi' not in results
    assert 'hubbard_matrices' not in results
    assert 'hubbard_structure' not in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
    })


def test_hp_initialization_only_mesh_more_points(
    aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_mesh_only, data_regression, tmpdir
):
    """Test an initialization only `hp.x` calculation with intersites with more points."""
    name = 'initialization_only_mesh_more_points'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    # QE generates the ``HUBBARD.dat``, but with empty values, thus we make sure the parser
    # does not recognize it as a final calculation and it does not crash as a consequence.
    attributes = {'retrieve_temporary_list': ['HUBBARD.dat']}
    node = generate_calc_job_node(
        entry_point_calc_job,
        aiida_localhost,
        test_name=name,
        inputs=generate_inputs_mesh_only,
        attributes=attributes,
        retrieve_temporary=(tmpdir, ['HUBBARD.dat'])
    )
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False, retrieved_temporary_folder=tmpdir)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message
    assert 'parameters' in results
    assert 'hubbard' not in results
    assert 'hubbard_chi' not in results
    assert 'hubbard_matrices' not in results
    assert 'hubbard_structure' not in results
    data_regression.check({
        'parameters': results['parameters'].get_dict(),
    })


def test_hp_failed_invalid_namelist(aiida_localhost, generate_calc_job_node, generate_parser, generate_inputs_default):
    """Test an `hp.x` calculation that fails because of an invalid namelist."""
    name = 'failed_invalid_namelist'
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    node = generate_calc_job_node(entry_point_calc_job, aiida_localhost, name, generate_inputs_default())
    parser = generate_parser(entry_point_parser)
    _, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_failed, calcfunction.exit_status
    assert calcfunction.exit_status == node.process_class.exit_codes.ERROR_INVALID_NAMELIST.status


@pytest.mark.parametrize(('name', 'exit_status'), (
    ('failed_no_hubbard_parameters', HpCalculation.exit_codes.ERROR_OUTPUT_HUBBARD_MISSING.status),
    ('failed_no_hubbard_chi', HpCalculation.exit_codes.ERROR_OUTPUT_HUBBARD_CHI_MISSING.status),
    ('failed_stdout_incomplete', HpCalculation.exit_codes.ERROR_OUTPUT_STDOUT_INCOMPLETE.status),
    ('failed_fermi_shift', HpCalculation.exit_codes.ERROR_FERMI_SHIFT.status),
    ('failed_out_of_walltime', HpCalculation.exit_codes.ERROR_OUT_OF_WALLTIME.status),
    ('failed_computing_cholesky', HpCalculation.exit_codes.ERROR_COMPUTING_CHOLESKY.status),
    ('failed_missing_chi_matrices', HpCalculation.exit_codes.ERROR_MISSING_CHI_MATRICES.status),
    ('failed_incompatible_fft_grid', HpCalculation.exit_codes.ERROR_INCOMPATIBLE_FFT_GRID.status),
))
def test_failed_calculation(
    generate_calc_job_node,
    generate_parser,
    generate_inputs_default,
    name,
    exit_status,
):
    """Test calculation failing with the correct exit status when detecing error messages."""
    entry_point_calc_job = 'quantumespresso.hp'
    entry_point_parser = 'quantumespresso.hp'

    node = generate_calc_job_node(entry_point_calc_job, test_name=name, inputs=generate_inputs_default())
    parser = generate_parser(entry_point_parser)
    _, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_failed, calcfunction.exit_status
    assert calcfunction.exit_status == exit_status
