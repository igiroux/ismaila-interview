# Auchan:Direct tech interview

Come and help us build an e-commerce website focused on user experience

## Guidelines

- [duplicate](https://help.github.com/articles/duplicating-a-repository/) this repository (do **not** fork it)
- solve the levels in ascending order
- commit at the very least at the end of each level

## What we expect

- clean code
- tests
- comments when you need to clarify a design decision or assumptions about the spec
- a simple way to run the code and the tests

## Acknowledgements

This test is shamelessly inspired by the drivy tech interview, which I found really great :)


## Test solution

### Installation in development mode

Just create a Python > 3.4 virtualenv.

```bash
virtualenv --python=$(which python3) venv
source venv/bin/activate
pip install -r requirements-dev
```

### Run tests

```bash
py.test -q zenmarket --cov=.
```

### Play with zenmarket command line interface

```bash
for i in $(seq 1 3)
do
    cat level${i}/data.json | zm-cli level${i} - - | \
        diff - level${i}/output.json && \
        echo "=== Done for level${i} === " ;
done
```

### Play with zenmarket server

You need two terminal sessions


```bash
# Session #1
zm-cli server  # run zenmarket server on default port 8888
```

```bash
# Session #2
curl -F data=@level1/data.json -w '\n' 'http://127.0.0.1:8888/api/level1/price' -H 'ContentType application/json'
```
