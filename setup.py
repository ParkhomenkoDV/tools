from setuptools import setup, find_packages
import time

name = 'tools'

Y, m, d, H, M, S = time.strftime('%Y.%m.%d.%H.%M.%S', time.localtime()).split('.')
H, M, S = str(int(H) + 1), str(int(M) + 1), str(int(S) + 1)
if len(H) == 1: H = '0' + H
if len(M) == 1: M = '0' + M
if len(S) == 1: S = '0' + S
version = '.'.join([Y, M, d, H, M, S])  # для предотвращения конфликта .00.

with open('README.md', 'rt', encoding='utf-8') as file:
    long_description = file.read()

with open('requirements.txt', 'rt') as file:
    install_requires = file.readlines()

setup(
    name=name,
    version=version,
    description='lib',
    long_description=long_description,
    long_description_content_type='text/markdown',  # если long_description = .md
    author='Daniil Andryushin',
    author_email='',
    url='https://github.com/ParkhomenkoDV/python_scripts',
    packages=[name],
    python_requires='>=3.8',
    install_requires=install_requires,
)
