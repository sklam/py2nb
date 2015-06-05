# PY2NB: Python To Notebook Converter

This is a small utility for turning python scripts into jupyter notebooks and
convert module-level multiline (triple quote) string literals into markdown
cells.  

## Why?

I wanted a tool to create user examples that can be executed as normal python
scripts so that they can be copy-and-pasted easily and can be rendered as
notebook for better readability (e.g nice styling, results embedded).

Also,

* Notebooks are nice to look at but slow to write
* Notebooks does not play well with version control


## Install

```bash
python setup.py install
```

## Usage


To convert a python script into a notebook:

```bash

python -m py2nb input.py output.ipynb
```

### Additional commandline not from this package

Execute a notebook:

```bash
ipython nbconvert --to=notebook --execute input.ipynb
```

Convert a notebook to a HTML:

```bash
ipython nbconvert --to=html input.ipynb
```


## Samples

See "samples" directory.



## How?

Uses python ``tokenize`` (builtin tokenizer library) for tokenization.
String literals with triple quote at column zero are converted into a comment
token with special ``<markdowncell>`` and ``<codecell>`` to feed into the python
importer in IPython version 3.  The processed tokens are untokenized using the
``tokenize`` module so that untouched line looks exactly the same as the input.
