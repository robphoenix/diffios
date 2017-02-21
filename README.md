# diffios

> Compare Cisco IOS configurations against a baseline.

[![Travis](https://img.shields.io/travis/robphoenix/diffios.svg?style=flat-square)](https://travis-ci.org/robphoenix/diffios)
[![PyPI](https://img.shields.io/pypi/v/diffios.svg?style=flat-square)](https://pypi.python.org/pypi/diffios)
[![PyPI](https://img.shields.io/pypi/pyversions/diffios.svg?style=flat-square)](https://pypi.python.org/pypi/diffios)
[![PyPI](https://img.shields.io/pypi/status/diffios.svg?style=flat-square)](ttps://pypi.python.org/pypi/diffios)
[![Coveralls](https://img.shields.io/coveralls/robphoenix/diffios.svg?style=flat-square)](https://coveralls.io/github/robphoenix/diffios?branch=master)

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

## Usage examples

> baseline.txt

```
version 15.3
!
hostname ABC{{ SITE_ID }}RT01
!
!
ip domain name diffios.dev
!
username admin privilege 15 secret 5 {{SECRET}}
!
interface Loopback0
 ip address {{LOOPBACK_IP}} 255.255.255.255
!
!
interface FastEthernet0/1
 description *** Link to Core ***
 ip address {{ FE_01_IP_ADDRESS }} 255.255.255.0
 duplex auto
 speed auto
!
interface FastEthernet0/2
 no ip address
 shutdown
!
interface Vlan100
 description User
 ip address {{ VLAN100_IP}} 255.255.255.0
!
interface Vlan200
 description Corporate
 ip address {{ VLAN200_IP }} 255.255.255.0
 no shutdown
!
!
line vty 0 4
 exec-timeout 5 0
 login local
 transport input ssh
 transport output ssh
!
!
end
```

> device_01.txt

```
Building configuration...

Current configuration : 1579 bytes
!
! Last configuration change at 12:32:40 UTC Thu Oct 27 2016
! NVRAM config last updated at 16:10:30 UTC Tue Nov 8 2016 by admin
version 15.3
!
hostname ABC12345RT01
!
!
ip domain name diffios.dev
!
interface Loopback0
 ip address 192.168.100.1 255.255.255.255
!
!
interface FastEthernet0/1
 description *** Link to Core ***
 ip address 192.168.0.1 255.255.255.128
 duplex auto
 speed auto
!
interface FastEthernet0/2
 no ip address
 shutdown
!
interface Vlan100
 description User
 ip address 10.10.10.1 255.255.255.0
!
interface Vlan300
 description Corporate
 ip address 10.10.10.2 255.255.255.0
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 192.168.0.2
!
!
line vty 0 4
 exec-timeout 5 0
 login local
 transport input telnet ssh
 transport output telnet ssh
!
!
end
```

> ignore.txt

```
Building configuration...
Current configuration
Last configuration change
NVRAM config last updated
```

## Development setup

To run the test suite

```sh
git clone https://github.com/robphoenix/diffios
cd diffios
# Here you may want to set up a virtualenv
make init
make test
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct, and the process for submitting pull requests.

## Authors

* **Rob Phoenix** - *Initial work* - [robphoenix](https://robphoenix.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
