from distutils.core import setup

setup(
    name='pyimmatcher',
    version='1.0',
    packages=['pyimmatcher', 'pyimmatcher.api', 'pyimmatcher.basic'],
    package_dir={'': 'src'},
    url='',
    license='Free and Open',
    author='Jacob Zimmerman',
    author_email='jacobz_20@yahoo.com',
    description='Python version of immatcher, a testing matcher library based on immutable matchers (called Assertions) returning a TestResult rather than being polled for each step, like Hamcrest.'
)
