# Please make sure environment variable COVERALLS_REPO_TOKEN exists and is correct.
# Reference: http://levibostian.com/python-code-coverage-and-coveralls-io/
pip install -r test_requirements.txt
nosetests -w test --with-coverage
coveralls