# irs-xml-tools

Python scripts to process [IRS 990 XML data](https://aws.amazon.com/public-datasets/irs-990/)

## Overview

## Run

```
pip install -r requirements.txt
```

## Develop

Include tests alongside your modules by adding `_test` to its name.

Run tests with `nosetests`.

Get coverage reports for all modules by running:

```
nosetests --with-coverage --cover-package=`find . -name '*.py' | sed 's/^\.\///' | sed 's/\.py$//' | grep -v _test.py | paste -s -d, -`
```
