"""Module with utilities for the CLI to generate default values."""


def get_hubbard_structure():
    """Return a ``HubbardStructureData`` representing bulk LiCoO2 with an initialized on-site Hubbard U on cobalt.

    The database will first be queried for the existence of such a structure. If this is not the case, one is created
    and stored. This function should be used as a default for CLI options that require a ``HubbardStructureData`` node.
    This way new users can launch the command without having to construct or import a structure first. This is the
    reason that we hardcode a LiCoO2 crystal to be returned: it is the prototypical example of the Quantum ESPRESSO
    ``hp.x`` documentation. More flexibility is not required for this purpose.

    :return: the UUID of a ``HubbardStructureData`` representing bulk LiCoO2
    """
    from aiida.orm import QueryBuilder
    from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData

    # Filters that will match any LiCoO2 structure with 4 sites and 3 kinds in total
    filters = {
        'attributes.sites': {'of_length': 4},
        'attributes.kinds': {'of_length': 3},
        'attributes.kinds.0.symbols.0': 'Co',
    }

    builder = QueryBuilder().append(HubbardStructureData, filters=filters)
    structure = builder.first(flat=True)

    if not structure:
        a, b, c, d = 1.40803, 0.81293, 4.68453, 1.62585
        cell = [[a, -b, c], [0.0, d, c], [-a, -b, c]]
        sites = [
            ('Co', 'Co', (0.0, 0.0, 0.0)),
            ('O', 'O', (0.0, 0.0, 3.6608)),
            ('O', 'O', (0.0, 0.0, 10.392)),
            ('Li', 'Li', (0.0, 0.0, 7.0268)),
        ]
        structure = HubbardStructureData(cell=cell, sites=sites)
        structure.initialize_onsites_hubbard('Co', '3d', 5.0)
        structure.store()

    return structure.uuid
