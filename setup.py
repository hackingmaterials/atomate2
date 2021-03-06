from pathlib import Path

from setuptools import find_packages, setup

module_dir = Path(__file__).resolve().parent

with open(module_dir / "README.md") as f:
    long_description = f.read()

if __name__ == "__main__":
    setup(
        name="atomate2",
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
        description="atomate2 is a library of materials science workflows",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/hackingmaterials/atomate2",
        author="Alex Ganose",
        author_email="alexganose@gmail.com",
        license="modified BSD",
        keywords="high-throughput automated workflow dft vasp",
        package_dir={"": "src"},
        package_data={"atomate2": ["py.typed"]},
        packages=find_packages("src"),
        data_files=["LICENSE"],
        zip_safe=False,
        include_package_data=True,
        install_requires=[
            "pymatgen>=2019.11.11",
            "custodian>=2019.8.24",
            "pydantic",
            "monty",
            "jobflow",
            "numpy",
            "emmet-core>=0.2.1",
        ],
        extras_require={
            "docs": [
                "sphinx==3.5.3",
                "furo==2021.3.20b30",
                "m2r2==0.2.7",
                "ipython==7.24.1",
                "nbsphinx==0.8.6",
                "nbsphinx-link==1.3.0",
                "FireWorks==1.9.7",
            ],
            "tests": [
                "pytest==6.2.4",
                "pytest-cov==2.11.1",
                "FireWorks==1.9.7",
                "matplotlib==3.4.2",
            ],
            "dev": ["pre-commit>=2.12.1"],
            "plotting": ["matplotlib"],
            "rtransfer": ["paramiko>=2.4.2"],
            "phonons": ["phonopy>=1.10.8"],
        },
        classifiers=[
            "programming language :: python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Information Technology",
            "Operating System :: OS Independent",
            "Topic :: Other/Nonlisted Topic",
            "Topic :: Scientific/Engineering",
        ],
        python_requires=">=3.7",
        tests_require=["pytest"],
    )
