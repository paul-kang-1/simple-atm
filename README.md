# Simple ATM Controller

The three classes (`Account`, `Bank` and `Controller`) in the `controller`
module provides essential features required for implementing an ATM. With the
absence of a persistent database, data relations are expressed through classes
and data structures in Python.

## Getting Started

### Prerequisites

The test suite make use of `pytest` and `pytest-cov` packages to perform tests
and genrate coverage reports. They can be installed through the command below:

```python
pip install -r requirements.txt
```

### Installation

No additional action is required to install the controller.

## Running the tests

All tests are located in `controller_test` module, and a command line coverage
report can be generated with `pytest` and `pytest-cov` through the following
command:

```python
pytest --cov=controller test_controller.py
```

A more detailed html file report can be generated through the following command:

```python
pytest --cov=controller --cov-report=html test_controller.py
```
