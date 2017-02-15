```
      _|  _|      _|_|      _|_|  _|
  _|_|_|        _|        _|            _|_|      _|_|_|
_|    _|  _|  _|_|_|_|  _|_|_|_|  _|  _|    _|  _|_|
_|    _|  _|    _|        _|      _|  _|    _|      _|_|
  _|_|_|  _|    _|        _|      _|    _|_|    _|_|_|
```


# diffios

> Compare Cisco IOS configurations against a baseline.

[![PyPI](https://img.shields.io/pypi/v/diffios.svg)](https://pypi.python.org/pypi/diffios) [![stability-unstable](https://img.shields.io/badge/stability-unstable-yellow.svg)](https://github.com/emersion/stability-badges#unstable) [![Build Status](https://travis-ci.org/robphoenix/diffios.svg?branch=master)](https://travis-ci.org/robphoenix/diffios) [![PyPI](https://img.shields.io/pypi/dm/diffios.svg)](https://pypi.python.org/pypi/diffios) [![Coverage Status](https://coveralls.io/repos/github/robphoenix/diffios/badge.svg?branch=master)](https://coveralls.io/github/robphoenix/diffios?branch=master) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/04b61eeff2484472b673079338c87c4a/badge.svg)](https://www.quantifiedcode.com/app/project/04b61eeff2484472b673079338c87c4a)

diffios is a Python library that compares Cisco IOS configurations, outputting
the lines of configuration which are additional and which are missing. It
respects the hierarchical nature of Cisco IOS configurations, uses variables
for elements that are expected to differ per config, such as ip addresses, and
can ignore junk lines. Its goal is to make the compliance auditing of large
network estates more manageable.

## Installation

Install via pip

```sh
pip install diffios
```

## Usage example


## Development setup

To run the test suite

```sh
git clone https://github.com/robphoenix/diffios
cd diffios
# Here you may want to set up a virtualenv
make init
make test
```

## Contributing (TODO)

Please read [CONTRIBUTING.md]() for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Rob Phoenix** - *Initial work* - [robphoenix](https://robphoenix.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
