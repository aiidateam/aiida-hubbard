## v0.4.0

Minor release that fixes the on-the-fly determination of intersite Hubbard parameters. This comes with an update of the `aiida-quantumespresso` plugin.

### 🐛 Bug fixes

* `Hubbard`: fix on-the-fly determination of V pairs  [[7303763](https://github.com/aiidateam/aiida-hubbard/commit/73037632e845926c369d82b336bef388a9ddc41a)]

### ⬆️ Update dependencies

* `Hubbard`: fix on-the-fly determination of V pairs  [[7303763](https://github.com/aiidateam/aiida-hubbard/commit/73037632e845926c369d82b336bef388a9ddc41a)]



## v0.3.0

Minor release that mainly supports the new version of `aiida-core` v2.7 and above.

### 📚 Documentation

* `Docs`: update compatibilit matrix  [[feaa40f](https://github.com/aiidateam/aiida-hubbard/commit/feaa40f4ba9b25f4197a9f5634b59f3d87298b71)]
* Update the reference with peer-reviewed article  [[fc0d2cf](https://github.com/aiidateam/aiida-hubbard/commit/fc0d2cf50020117944c9cc5e729051c665f36f9c)]
* Docs: fix some old typos  [[c85ff8d](https://github.com/aiidateam/aiida-hubbard/commit/c85ff8ded23861c12881152e485875653710f989)]

### 🔧 Maintenance

* DevOps: stick to PEP 404 for version identification  [[55b8b0d](https://github.com/aiidateam/aiida-hubbard/commit/55b8b0d7c3ad53f232c602ef22d37170a61a1599)]

### ⬆️ Update dependencies

* Deps: allow aiida-core version 2.7 or higher  [[f0d2fb8](https://github.com/aiidateam/aiida-hubbard/commit/f0d2fb862ad9cf613cce3cb04b95c399b9a4ec0b)]



## v0.2.0

This version of the plugin comes mainly with a breaking change with the protocol parameters, to align with a recent work devising improved protocols and better naming:

> G. d. M. Nascimento, F. J. d. Santos, M. Bercx, D. Grassano, G. Pizzi, and N. Marzari, [_"Accurate and efficient protocols for high-throughput first-principles materials simulations"_](https://arxiv.org/abs/2504.03962), (2025)

This is also to align with `aiida-quantumespresso` updates.

### ‼️ Breaking changes

* Dependencies: update protocol names  [[fe3cca2](https://github.com/aiidateam/aiida-hubbard/commit/fe3cca27aade49c56947eb9d071a1573db2e0d09)]

### 🐛 Bug fixes

* `HpCalculation`: fix error message for exit code 495  [[b8e68a9](https://github.com/aiidateam/aiida-hubbard/commit/b8e68a9f0193aa33d97784e43b8f8caa73ba0695)]

### 📚 Documentation

* `Docs`: fix title of main reference paper  [[006b9e5](https://github.com/aiidateam/aiida-hubbard/commit/006b9e562f05c041e4e578b745c41f2e23d06821)]
* Docs: update citation of main paper with arxiv reference [[d3a2515](https://github.com/aiidateam/aiida-hubbard/commit/d3a25152e17b19f621dc7ae57eb96a77149dbe87)]
* Docs: replace markdown emoji strings with symbols [[ce99678](https://github.com/aiidateam/aiida-hubbard/commit/ce99678906fd16073e21308b3b14774654809862)]
* :books: Docs: add precompiled outputs to tutorial notebooks  [[2a42fe4](https://github.com/aiidateam/aiida-hubbard/commit/2a42fe413e9b6c947829bd5b4c94b0732eb947d1)]

### 🔧 Maintenance

* DevOps: update github actions version  [[d7ace7c](https://github.com/aiidateam/aiida-hubbard/commit/d7ace7ca8a010309b1a4eca0b7aae16deab27537)]

### ⬆️ Update dependencies

* Dependencies: update protocol names  [[fe3cca2](https://github.com/aiidateam/aiida-hubbard/commit/fe3cca27aade49c56947eb9d071a1573db2e0d09)]


## v0.1.0:
First official release of `aiida-hubbard`, the official plugin for the HP code of Quantum ESPRESSO to the AiiDA platform.
The following calculations, parsers, and workflows are provided:

### Calculations
- `HpCalculation`: calculation plugin for `hp.x`

### Parsers
- `HpParser`: parser for the `hp.x` calculation

### Workflows
- `HpBaseWorkChain`: workflow to run a `HpCalculation` to completion
- `HpParallelizeAtomsWorkChain`: workflow to parallelize an `hp.x` calculation as independent atoms child subprocesses
- `HpParallelizeQpointsWorkChain`: workflow to parallelize an `HpParallelizeAtomsWorkChain` calculation as independent q-points child subprocesses
- `HpWorkChain`: workflow to run a manage parallel capabilities of `hp.x`, by proprerly calling the correct workchains
- `SelfConsistentHubbardWorkChain`: worfklow to calculate self-consistently the Hubbard parameters with on-the-fly nearest neighbours detection
