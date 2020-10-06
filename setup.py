import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='drf-react-template-framework',
    version='0.0.1',
    description='Django REST Framework plugin that creates form schemas for react-jsonschema-form',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yoyowallet/drf-react-template-framework',
    author='Stuart Bradley',
    author_email='stuart@yoyowallet.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Framework :: Django',
    ],
    keywords='drf react',
    packages=setuptools.find_packages(
        include=['drf_react_template', 'drf_react_template.*']
    ),
    install_requires=['djangorestframework>=3.12'],
    python_requires='>=3.7',
)
