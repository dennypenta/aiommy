from setuptools import setup


with open('README.md', encoding='utf-8') as f:
    long_description=f.read()

setup(
    name='aiommy',
    version='0.0.2',

    description='A helpful tools for building web API',
    long_description=long_description,

    url='https://github.com/dennypenta/aiommy',

    author='Denis Dvornikov',
    author_email='candyboobers@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='Web API',

    packages=['aiommy'],

    install_requires=['aiohttp', 'cerberus', 'pytz', 'peewee', 'peewee_async', 'PyJWT', 'psycopg2', 'aiopg']
)
