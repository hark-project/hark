import pip.req
import setuptools
import sys


def install_reqs():
    reqs = pip.req.parse_requirements('requirements.txt', session=False)
    reqs = [str(ir.req) for ir in reqs]
    return reqs


def test_reqs():
    reqs = pip.req.parse_requirements('requirements-dev.txt', session=False)
    reqs = [str(ir.req) for ir in reqs]

    if sys.version_info.major == 2:
        # needed for python2 only
        reqs27 = pip.req.parse_requirements(
            'requirements-dev-py27.txt', session=False)
        reqs27 = [str(ir.req) for ir in reqs27]
        reqs.extend(reqs27)

    return reqs


setuptools.setup(
    name='hark',
    version='v1.0.0-dev',

    packages=setuptools.find_packages(exclude=('tests')),

    install_requires=install_reqs(),
    tests_require=test_reqs(),

    include_package_data=True,

    # entry_points={
    #    'console_scripts': [
    #        'hark = hark.cli.hark:hark_main',
    #        'hark_imagestore = hark.cli.hark_imagestore:hark_imagestore'
    #    ]
    # },

    scripts=[
        'bin/hark',
        'bin/hark_imagestore',
    ],

    zip_safe=True,

    license='GNU Affero General Public License v3 (GPLv3)',

    # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: Pre-Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='virtualization development OS',
)
