import multiprocessing, logging # Fix atexit bug
from setuptools import setup, find_packages


setup(
        name='git-prompt',
        version='0.0.1-dev',
        author="Jacob Alheid",
        author_email="shakefu@gmail.com",
        packages=find_packages(),
        entry_points={
            'console_scripts':[
                'gitprompt = gitprompt:main',
                ],
            },
        )


