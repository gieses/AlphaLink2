# Copyright 2022 DP Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Install script for setuptools."""

from setuptools import find_packages
from setuptools import setup

setup(
    name="alphalink2",
    version="1.0",
    description="Modelling protein complexes with crosslinking mass spectrometry and deep learning",
    author="Kolja Stahl",
    license="Apache License, Version 2.0",
    url="https://github.com/Rappsilber-Laboratory/AlphaLink2",
    packages=find_packages(
        exclude=["scripts", "tests", "example_data", "docker", "benchmark", "img", "evaluation", "notebooks"]
    ),
    entry_points={
        "console_scripts": [
            "alphalink2-crosslinks=alphalink.scripts.alphalink_generate_crosslinks:main",
            "alphalink2-msa=alphalink.scripts.alphalink_msa:main",
            "alphalink2-inference=alphalink.scripts.alphalink_inference:main",
            "alphalink2-wf=alphalink.scripts.alphalink_wf:main",
        ]},

    install_requires=[
        "absl-py",
        "biopython",
        "ml-collections",
        "numpy",
        "pandas",
        "scipy",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
