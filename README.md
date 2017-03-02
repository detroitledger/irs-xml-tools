# irs-xml-tools

Python scripts to process [IRS 990 XML data](https://aws.amazon.com/public-datasets/irs-990/)

## Overview

Read about the 990 data at the IRS's amazon page: https://aws.amazon.com/public-datasets/irs-990/

In short, the IRS has posted (as of March 1 2017) about 59 gigabytes of XML files that represent tax-exempt organization's Form 990 filings.

The filings are inventoried by year in JSON index files, with names like `index_2012.json`. The filings themselves have names like `201017793492000000_public.xml`.

There are seventeen separate schemas used. Check out [the archive.org mirror of the data](https://archive.org/download/IRS990-efile) to download just the `.xsd` schema information -- it also has HTML-formatted diffs.

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
