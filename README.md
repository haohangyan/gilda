# Gilda: Grounding Integrating Learned Disambiguation
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![Build](https://github.com/indralab/gilda/actions/workflows/tests.yml/badge.svg)](https://github.com/indralab/gilda/actions)
[![Documentation](https://readthedocs.org/projects/gilda/badge/?version=latest)](https://gilda.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/gilda.svg)](https://badge.fury.io/py/gilda)

Gilda is a Python package and REST service that grounds (i.e., finds
appropriate identifiers in namespaces for) named entities in biomedical text.

## Installation
Gilda is deployed as a web service at http://grounding.indra.bio/ (see
Usage instructions below), however, it can also be used locally as a Python
package.

The recommended method to install Gilda is through PyPI as
```bash
pip install gilda
```
Note that Gilda uses a single large resource file for grounding, which is
automatically downloaded into the `~/.data/gilda/<version>` folder during
runtime (see [pystow](https://github.com/cthoyt/pystow#%EF%B8%8F-configuration) for options to
configure the location of this folder).

Given some additional dependencies, the grounding resource file can
also be regenerated locally by running `python -m gilda.generate_terms`.

## Documentation and notebooks
Documentation for Gilda is available [here](https://gilda.readthedocs.io).
[This notebook](https://github.com/indralab/gilda/blob/master/notebooks/gilda_introduction.ipynb) provides an interactive tutorial for using Gilda, and
[this notebook](https://github.com/indralab/gilda/blob/master/notebooks/custom_grounders.ipynb) shows several examples of how Gilda can be instantiated with custom
grounding resources. Finally, [this notebook](https://github.com/indralab/gilda/blob/master/models/model_training.ipynb) provides interactive sample code for training
new disambiguation models.

## Usage
Gilda can either be used as a REST web service or used programmatically
via its Python API. An introduction Jupyter notebook for using Gilda
is available at
https://github.com/indralab/gilda/blob/master/notebooks/gilda_introduction.ipynb

### Use as a Python package
For using Gilda as a Python package, the documentation at
http://gilda.readthedocs.org provides detailed descriptions of each module of
Gilda and their usage. A basic usage example is as follows

```python
import gilda
scored_matches = gilda.ground('ER', context='Calcium is released from the ER.')
```

### Use as a web service
The REST service accepts POST requests with a JSON header on the /ground
endpoint. There is a public REST service running at http://grounding.indra.bio
but the service can also be run locally as

```bash
python -m gilda.app
```
which, by default, launches the server at `localhost:8001` (for local usage
replace the URL in the examples below with this address).

Below is an example request using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "kras"}' http://grounding.indra.bio/ground
```

The same request using Python's request package would be as follows:

```python
import requests
requests.post('http://grounding.indra.bio/ground', json={'text': 'kras'})
```

## Run web service with Docker

After cloning the repository locally, you can build and run a Docker image
of Gilda using the following commands:

```shell
$ docker build -t gilda:latest .
$ docker run -d -p 8001:8001 gilda:latest
```

Alternatively, you can use `docker-compose` to do both the initial build and
run the container based on the `docker-compose.yml` configuration:

```shell
$ docker-compose up
```

## Citation

```bibtex
@article{gyori2021gilda,
  author = {Gyori, Benjamin M and Hoyt, Charles Tapley and Steppi, Albert},
  doi = {10.1101/2021.09.10.459803},
  journal = {bioRxiv},
  publisher = {Cold Spring Harbor Laboratory},
  title = {{Gilda: biomedical entity text normalization with machine-learned disambiguation as a service}},
  url = {https://www.biorxiv.org/content/10.1101/2021.09.10.459803v1},
  year = {2021}
}
```

## Funding
The development of Gilda was funded under the DARPA Communicating with Computers
program (ARO grant W911NF-15-1-0544) and the DARPA Young Faculty Award
(ARO grant W911NF-20-1-0255).
