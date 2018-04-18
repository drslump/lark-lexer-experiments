from distutils.command.build import build
from distutils.core import setup, Extension, Command

import sys, subprocess


class MyBuild(build):
    def run(self):
        print('Generating lexer.c...')
        subprocess.check_output(['re2c', '-r', '-o', 'lexer.c', 'lexer.re'])

        print('Generating FSM lexers...')
        with open('re2c_lexer.py', 'w') as fd:
            fd.write(subprocess.check_output(['python', '-m', 're2c', 'grammar.g']))
        with open('re2c_py_lexer.py', 'w') as fd:
            fd.write(subprocess.check_output(['python', '-m', 're2c', 'python2.g']))

        build.run(self)

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(['benchmark.py'])
        raise SystemExit(errno)


setup(
    name="lark_lexer_experiments",
    version="1.0",
    install_requires=[
        "lark-parser==0.5.6",
        'pytest',
        'pytest-benchmark'
    ],
    test_suite='benchmark.py',
    cmdclass={
      'build': MyBuild,
      'test': PyTest,
    },
    ext_modules=[
      Extension('_lexer', ['lexer.c'])
    ]
)
