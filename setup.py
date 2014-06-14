__doc__ = open('README.md').read()

from setuptools import setup

setup(name='ido',
    version='0.1',
    description="A command tool used to install packages and execute commands.",
    long_description=__doc__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    packages = ['ido'],
    platforms = 'any',
    keywords='command tools',
    author='limodou',
    author_email='limodou@gmail.com',
    url='https://github.com/limodou/ido',
    license='BSD',
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'ido = ido:main',
        ],
    },
    install_requires=['future', 'colorama']
)
