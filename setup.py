import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='recipe_recommender',
        description='Recipe recommender',
        author_email='nashjea@gmail.com',
        url="https://github.com/janash/recipe_recommender",
        license='BSD-3C',
        packages=setuptools.find_packages(),
        install_requires=[
            'beautifulsoup4',
            'pandas>=0.18',
            'requests',
            'sqlalchemy',
        ],
        extras_require={
            'docs': [
                'sphinx==1.2.3',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'tox',
            ],
        },

        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=True,
    )
