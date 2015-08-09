# Please make sure environment variable COVERALLS_REPO_TOKEN exists and is correct.
# Reference: http://levibostian.com/python-code-coverage-and-coveralls-io/
pip install -q -r test_requirements.txt
mkdir -p reports/coverage_html
nosetests -w test --with-coverage
nosetests -w test --with-coverage --cover-erase --with-xunit --with-json-extended
coverage html -d reports/coverage_html
coveralls
