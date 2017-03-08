.. image:: https://raw.githubusercontent.com/robphoenix/diffios/master/docs/_static/logo.png
    :target: https://diffios.readthedocs.io/en/latest/


diffios is a Python library that provides a way to compare Cisco IOS configurations
against a baseline template, and generate an output detailing the differences
between them.

Where more traditional diff tools, such as Python's `difflib <https://docs.python.org/3.6/library/difflib.html>`_
library, consider lines independently and their order as important, diffios
considers hierarchical configuration blocks independently and pays no mind to
the order of the lines, only whether they are present or not, in the same way a
Cisco device would.

This means we can declare our expectations in a baseline template, and then
compare our device configurations against it. diffios will generate an output
which details where our device configurations differ from our expectations.
For elements we expect to vary, such as hostnames and IP addresses, diffios
makes use of variables, and will ignore pre-defined junk lines that bear no
relevance on our configuration.

The goal of diffios is to make the compliance auditing of large network estates
more manageable.


.. image:: https://img.shields.io/travis/robphoenix/diffios.svg?style=flat-square
   :target: https://travis-ci.org/robphoenix/diffios

.. image:: https://img.shields.io/pypi/v/diffios.svg?style=flat-square
   :target: https://pypi.python.org/pypi/diffios

.. image:: https://img.shields.io/pypi/pyversions/diffios.svg?style=flat-square
   :target: https://pypi.python.org/pypi/diffios

.. image:: https://img.shields.io/pypi/status/diffios.svg?style=flat-square
   :target: https://pypi.python.org/pypi/diffios

.. image:: https://img.shields.io/coveralls/robphoenix/diffios.svg?style=flat-square
   :target: https://coveralls.io/github/robphoenix/diffios?branch=master

.. image:: https://readthedocs.org/projects/diffios/badge/?version=latest&style=flat-square
   :target: http://diffios.readthedocs.io/en/latest/?badge=latest

Installation
------------

Install via pip

.. code:: bash

    pip install diffios

Usage examples
--------------

We'll need a baseline template that we expect all of our devices to conform to.
This can be any kind of text file, :code:`.txt`, :code:`.conf`, :code:`.cfg` or however
you store your device configuration files. It can also be a Python list if you
want.

Here we have a simple **baseline.txt** file.

.. code::

    version 15.3
    !
    hostname ABC{{ SITE_ID }}RT01
    !
    !
    ip domain name diffios.dev
    !
    username admin privilege 15 secret 5 {{ SECRET }}
    !
    interface Loopback0
     ip address {{ LOOPBACK_IP }} 255.255.255.255
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
     ip address {{ VLAN100_IP }} 255.255.255.0
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

Within this baseline file we can use variables, defined by the double curly
braces (:code:`{{  }}`), in place of changeable elements such as hostnames and
IP addresses.

We can then collect the output from a show run command from the device we want
to compare and save it in a file. Here we have a configuration file, **device_01.txt**,
that has a number of differences to our baseline.

.. code::

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
     ip address 192.168.0.2 255.255.255.0
     duplex auto
     speed auto
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

Device configurations can often contain junk lines that are going to show up as
differences but that really we don't care about. Lines such as :code:`Building configuration...`.

We can add these lines to a separate file that we pass to diffios as a list of
lines we'd like to ignore. Each line in this file will be evaluated as a regular
expression, so to match :code:`! NVRAM config last updated at 16:10:30 UTC Tue Nov 8 2016 by admin`
we only have to add something like :code:`NVRAM config last updated`.

This file can be named whatever you like, here we have quite sensibly named file
*ignore.txt*. This can also be a regular Python list.

.. code::

    Building configuration...
    Current configuration
    Last configuration change
    NVRAM config last updated

So, now that we have our configurations ready we can compare them.

.. code:: python

    >>> import diffios
    >>>
    >>> baseline = "baseline.txt"
    >>> comparison = "device_01.txt"
    >>> ignore = "ignore.txt"
    >>>
    # We initialise a diffios Compare() object with our three files.
    # The ignore file is optional, and defaults to an empty list.
    >>> diff = diffios.Compare(baseline, comparison, ignore)
    # From this Compare object we can see the differences between our
    # configurations using the delta() method.
    >>> print(diff.delta())
    --- baseline
    +++ comparison

    -   1: interface FastEthernet0/1
    -       ip address {{ FE_01_IP_ADDRESS }} 255.255.255.0
    -   2: interface FastEthernet0/2
    -       no ip address
    -       shutdown
    -   3: interface Vlan200
    -       description Corporate
    -       ip address {{ VLAN200_IP }} 255.255.255.0
    -       no shutdown
    -   4: line vty 0 4
    -       transport input ssh
    -       transport output ssh
    -   5: username admin privilege 15 secret 5 {{ SECRET }}

    +   1: interface FastEthernet0/1
    +       ip address 192.168.0.1 255.255.255.128
    +   2: interface FastEthernet0/2
    +       ip address 192.168.0.2 255.255.255.0
    +       duplex auto
    +       speed auto
    +   3: interface Vlan300
    +       description Corporate
    +       ip address 10.10.10.2 255.255.255.0
    +       no shutdown
    +   4: ip route 0.0.0.0 0.0.0.0 192.168.0.2
    +   5: line vty 0 4
    +       transport input telnet ssh
    +       transport output telnet ssh

The output above lists the lines of configuration that are missing from our
device but that are present in our baseline template, shown by lines prefixed
with a :code:`-`. Lines that are present in our device that are not in our baseline
template are prefixed with a :code:`+`. Each block is numbered and listed in context
with it's parent line. Currently this output doesn't signify whether the parent
line is part of the difference or only there to provide context.

We can also audit a large number of devices against a single baseline. Below is
an example script that checks every file within a given directory against a
baseline and stores the differences in a CSV file.

.. code:: python

    import os
    import csv

    import diffios

    IGNORE_FILE = os.path.join(os.getcwd(), "ignores.txt")
    COMPARISON_DIR = os.path.join(os.getcwd(), "configs", "comparisons")
    BASELINE_FILE = os.path.join(os.getcwd(), "configs", "baselines", "baseline.txt")

    # the CSV file we will write to
    output = os.path.join(os.getcwd(), "diffs.csv")

    with open(output, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        # write the headers
        csvwriter.writerow(["Comparison", "Baseline", "Additional", "Missing"])
        files = sorted(os.listdir(COMPARISON_DIR))
        for f in files:
            comparison_file = os.path.join(COMPARISON_DIR, f)
            # initialise the diffios Compare object
            diff = diffios.Compare(BASELINE_FILE, comparison_file, IGNORE_FILE)
            csvwriter.writerow([
                f,
                os.path.basename(BASELINE_FILE),
                # write the formatted differences to the csv file
                diff.pprint_additional(),
                diff.pprint_missing()
            ])

The pretty print methods used above format the data in a more readable manner.
We can compare the output from the :code:`additional()` method and the
:code:`pprint_additional()` method.

The :code:`additional()`, and :code:`missing()`, methods return a list of lists
that represent each block that contains a difference.

.. code:: python

    >>> from pprint import pprint
    >>> pprint(diff.additional())
    [['interface FastEthernet0/1', ' ip address 192.168.0.1 255.255.255.128'],
     ['interface FastEthernet0/2',
      ' ip address 192.168.0.2 255.255.255.0',
      ' duplex auto',
      ' speed auto'],
     ['interface Vlan300',
      ' description Corporate',
      ' ip address 10.10.10.2 255.255.255.0',
      ' no shutdown'],
     ['ip route 0.0.0.0 0.0.0.0 192.168.0.2'],
     ['line vty 0 4',
      ' transport input telnet ssh',
      ' transport output telnet ssh']]

Whereas the :code:`pprint_additional()` and :code:`print_missing()` methods return
strings that represent all the differences, with each block separated by a newline.

.. code:: python

    >>> print(diff.pprint_additional())
    interface FastEthernet0/1
     ip address 192.168.0.1 255.255.255.128

    interface FastEthernet0/2
     ip address 192.168.0.2 255.255.255.0
     duplex auto
     speed auto

    interface Vlan300
     description Corporate
     ip address 10.10.10.2 255.255.255.0
     no shutdown

    ip route 0.0.0.0 0.0.0.0 192.168.0.2

    line vty 0 4
     transport input telnet ssh
     transport output telnet ssh

Development setup
-----------------

To run the test suite

.. code:: bash

    git clone https://github.com/robphoenix/diffios
    cd diffios
    # Here you may want to set up a virtualenv
    make init # this will install, via pip, test & documentation dependencies
    make test # run pytest with configuration options in setup.cfg

Contributing
------------

Please read `CONTRIBUTING.md <https://github.com/robphoenix/diffios/blob/master/CONTRIBUTING.md>`_ for details on the code of conduct, and the process for submitting pull requests.

Authors
-------

* **Rob Phoenix** - *Initial work* - `robphoenix <https://robphoenix.com>`_

License
-------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/robphoenix/diffios/blob/master/LICENSE>`_ file for details

Logo
----

Arrows graphic by `Madebyoliver <http://www.flaticon.com/authors/madebyoliver>`_ from `Flaticon <http://www.flaticon.com/>`_ is licensed under `CC BY 3.0 <http://creativecommons.org/licenses/by/3.0/>`_. Made with `Logo Maker <http://logomakr.com>`_.
