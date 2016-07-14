# hark

[![Build Status](https://travis-ci.org/ceralena/hark.svg?branch=develop)](https://travis-ci.org/ceralena/hark)

**Please Note**: This project is a work in progress. It's only barely
functional and unlikely to be useful yet.

## Intro

Hark is a simple cross-platform tool for running virtual machines. It starts
VMs very quickly with a minimum of configuration.

Hark is influenced by [Vagrant](www.vagrantup.com). Hark is smaller
and less ambitious than Vagrant, providing for greater ease of use and
simplicity.

Hark is designed for:

1. students
2. rapid prototyping
3. anyone new to Linux and BSD operating systems

Hark stays small, simple and reliable by running only a prebuilt set of OS
images. These images are maintained directly by the project and tested
alongside the tool itself. Images are built with `packer`. Hark is able to find
and download images it hasn't cached locally from the web service hosted by the
project maintainers.

# License

GPLv3. See the LICENSE file for details.

# Installation


At the moment hark can only be installed from source, with Python. Using a Python
virtualenv is strongly recommended. After checking out the repo:

	cd src && pip install .

# Python Support

Hark only supports python 3.3 and up, because it uses the `yield from` syntax with `asyncio` coroutines.

It is tested in dev on these version:

* `2.7.11`
* `3.3.5`
* `3.4.3`
* `3.5.1`

And in travis on these versions:

* `2.7`
* `3.3`
* `3.4`
* `3.5`

# Running Tests

These instructions all assume that you're in the `src` dir.

Test dependencies are not installed by default:

	$ pip install -r req-*.txt

To test via setuptools:

	$ python setup.py test

### Tox

Tox can run tests across all supported Python versions. It also manages an
isolated Python virtual environment for each test. Just run:

	$ tox

To install tox:

	pip install tox==2.3.1

To install the appropriate versions of the Python interpreter, consider
[pyenv](https://github.com/yyuu/pyenv):

	$ for ver in 2.7.11 3.3.5 3.4.3 3.5.1; do
		pyenv install $ver
	done


## Coverage Report

You can generate a simple summary of coverage:

	$ py.test --cov=hark

Or an HTML report which you can view in your browser:

	$ py.test --cov=hark --cov-report=html
	$ (cd htmlcov; python3 -m http.server)
