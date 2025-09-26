"""
Setup script for LeadSprinter Pro
Professional LinkedIn Lead Generation Tool
"""

from cx_Freeze import setup, Executable
import sys
import os

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = {
    'packages': [
        'PySimpleGUI',
        'selenium', 
        'pandas',
        'openpyxl',
        'requests',
        'tqdm',
        'datetime',
        'logging',
        'threading',
        're',
        'random',
        'time',
        'urllib',
        'json'
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy.random._examples'
    ],
    'include_files': [
        ('README.md', 'README.md'),
        ('config.py', 'config.py'),
        ('utils.py', 'utils.py')
    ],
    'zip_include_packages': ['*'],
    'zip_exclude_packages': []
}

# GUI applications require a different base on Windows (the default is for
# console applications).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        'main.py',
        base=base,
        target_name='LeadSprinter-Pro',
        icon=None,  # Add icon file path here if you have one
        copyright='© 2025 LeadSprinter Development Team'
    )
]

setup(
    name='LeadSprinter Pro',
    version='1.0.0',
    description='Professional LinkedIn Lead Generation Tool',
    long_description=open('README.md').read(),
    author='LeadSprinter Development Team',
    author_email='info@leadsprinter.com',
    url='https://leadsprinter.com',
    license='Commercial',
    options={'build_exe': buildOptions},
    executables=executables,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Office/Business :: Groupware',
    ],
    keywords='linkedin, lead generation, scraping, automation, business',
)