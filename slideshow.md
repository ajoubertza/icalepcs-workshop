name: empty layout
layout: true

---
name: title
class: center, middle

PyTango and Fandango Workshop
=============================

[Anton Joubert](https://github.com/ajoubertza) - [Sergi Rubio Manrique](https://github.com/sergirubio)

ICALEPCS 2019 - New York

*

GitHub: [ajoubertza/icalepcs-workshop](https://github.com/ajoubertza/icalepcs-workshop)

Slides: [https://ajoubertza.github.io/icalepcs-workshop](https://ajoubertza.github.io/icalepcs-workshop)

---
name: acknowledgements
layout: true
class: middle

Acknowledgements
================

---

Much of the content of this presentation is from work by:

* [Vincent Michel](https://github.com/vxgmichel)
* [Tiago Coutinho](https://github.com/tiagocoutinho)
* [Antoine Dupré](https://github.com/AntoineDupre)

Thanks!

---
name: presentation
layout: true
class: middle

What is PyTango?
================

---

* Python library

* Binding over the C++ tango libray

* ... using boost-python

* relies on numpy

* Multi OS: Linux, Windows, Mac

* Works on python 2.7 .. 3.7

---

... plus some extras:

* Pythonic API

* asyncio and gevent event loop

* ITango (a separate project)

* ?? alternative TANGO Database server (sqlite, redis backends) ??

---

name: menu
class: middle
layout: true

What's on the menu?
===================

---

* A fresh python3 tango install using conda

* ITango, a powerful client interface

* Writing tango servers with 15 lines of python

* Testing our servers without a database

* New features being considered

* Fandango - the Swiss army knife

---

class: middle
layout: true

Playing with
============

---

.center[![conda](images/conda_logo.svg)]

### Conda is both:

* an open source package management system

* an environment management system

* it runs on Windows, macOS and Linux

---

class: middle
layout: true

Playing with conda
==================

---

### Requirements for this workshop:

* A 64 bits linux machine

* An internet connection

* A Tango database accessible (optional)

* No sudo access is required

---

### Installing miniconda:

``` bash
# Download the latest miniconda
$ wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
[...]

# Extract to a local directory (~/miniconda3)
$ bash Miniconda3-latest-Linux-x86_64.sh -b # No manual intervention
[...]

# Activate the conda environment
$ source ~/miniconda3/bin/activate

# Test python
(root) $ python
Python 3.6.2 |Anaconda, Inc.| (default, Sep 30 2017, 18:42:57)
[...]
```

`(root)` indicates we the main conda environment activated

---

### Creating a tango environment

``` bash
# Conda information
(root) $ conda info
[...]

# Create a python3 + tango envrionment
(root) $ conda create --name tango3 --channel tango-controls itango python=3
[...]

# Activate the tango3 environment
(root) $ source activate tango3

# Test itango
(tango3) $ itango
ITango 9.2.2 -- An interactive Tango client.
Running on top of Python 3.6.2, IPython 6.1 and PyTango 9.2.2
[...]
```

Checkout [anaconda.org/tango-controls](https://anaconda.org/tango-controls)

---

name: ITango
layout: true
class: middle

ITango
============

---

### Features

* IPython (jupyter) console

* Direct access to tango classes

* TANGO class sensitive device name auto-completion

* Event monitor

* Qt console

* Notebook

* User friendly error handling

---

### Hands on

``` bash
(tango3) $ conda install jupyter matplotlib
[...]
(tango3) $ jupyter notebook
```

```ipython
In [2]: tg_test = TangoTest("sys/tg_test/1")
[...]

```

---

### Plan B:

<a href="https://asciinema.org/a/0qfbv42rw496b942ny6lpdxrn">
   <img src="https://asciinema.org/a/0qfbv42rw496b942ny6lpdxrn.png"
   	style="display:block; margin:auto; width: 640px;"/>
</a>

---

name: Server
layout: true
class: middle

Wow! Writing device servers has never been so easy!
------------------

---

Device servers with pytango >=9.2.1

```python
from time import sleep
from tango.server import Device, attribute, command

class PowerSupply(Device):

    @attribute(dtype=float)
    def voltage(self):
        return 1.23

    @command
    def calibrate(self):
        sleep(0.1)

if __name__ == '__main__':
    PowerSupply.run_server()
```
---

layout: true

---
class: middle

# Testing time!

### Server:

```bash
$ python -m tango.test_context ps0.PowerSupply --host $(hostname)
Ready to accept request
PowerSupply started on port 8888 with properties {}
Device access: tango://yourhostname:8888/test/nodb/powersupply#dbase=no
Server access: tango://yourhostname:8888/dserver/PowerSupply/powersupply#dbase=no
```

### Client:

```bash
$ itango
ITango 9.2.2 -- An interactive Tango client.

In [1]: d = Device('tango://yourhostname:8888/test/nodb/powersupply#dbase=no')

In [2]: d.calibrate()

In [3]: d.voltage
Out[3]: 1.23
```

---
class: middle

Let's try out events!
---------------------

Adding a polled attribute:

```python
import random

[...]

    @attribute(
        dtype=float,
        polling_period=500,  # 0.5 seconds
        rel_change=1e-3)     # 0.1% relative change
    def random(self):
        return random.random()
```

Going back to ITango:

```python
In [4]: cb = tango.utils.EventCallback()

In [5]: eid = d.subscribe_event('random', tango.EventType.CHANGE_EVENT, cb)

2017-10-07 11:35:17.456138 TEST/NODB/POWERSUPPLY RANDOM#DBASE=NO CHANGE
... [ATTR_VALID] 0.9369674083770559
```

---
class: middle

Unit testing
------------

```python
from tango import DevState
from tango.test_utils import DeviceTestContext

from powersupply.powersupply import PowerSupply


def test_init():
    """Test device goes into STANDBY when initialised"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.Init()
        assert proxy.state() == DevState.STANDBY
```

`DeviceTestContext` launches tango device server in a subprocess,
and returns a `DeviceProxy` instance connected to it.

"Sort-of" unit testing - can test from client's perspective, but
cannot access device's methods or attributes directly.

---
class: middle

Asynchronous pytango
====================

#### Also called green modes, checkout the docs:

[pytango.readthedocs.io/en/stable/green_modes/green.html](http://pytango.readthedocs.io/en/stable/green_modes/green.html)

---
class: middle

Gevent client mode example
-------------------------

``` bash
# Install gevent
$ conda install gevent
[...]

# Run python
$ python
```

``` python
>>> # Import from tango.gevent
>>> from tango.gevent import DeviceProxy

>>> # Create proxy (uses gevent)
>>> dev = DeviceProxy("sys/tg_test/1")

>>> # Read the state asynchronously
>>> result = dev.state(wait=False)
>>> result
<gevent.event.AsyncResult at 0x1a74050>

>>> # Wait for the result
>>> state = result.get()
>>> print(state)
RUNNING
```
---
class: middle

Asyncio client mode example
---------------------------

```bash
# Install an asyncio console
$ pip install aioconsole
[...]

# Run apython
$ apython
[...]
```

```python
>>> # Import from tango.asyncio
>>> from tango.asyncio import DeviceProxy as asyncio_proxy

>>> # Create proxy
>>> device = await asyncio_proxy('sys/tg_test/1')

>>> # Read attribute
>>> result = await device.read_attribute('ampli')
>>> result.value
1.23
```

---
class: middle

A simple TCP server for tango attributes
----------------------------------------

- Try this [simple TCP server for Tango attributes](https://github.com/tango-controls/pytango/blob/develop/examples/asyncio_green_mode/tcp_server_example.py)

- It runs on all interfaces on port 8888:

    ```bash
    $ python tango_tcp_server.py
    Serving on 0.0.0.0 port 8888
    ```

- It can be accessed through netcat:

    ```bash
    $ ncat localhost 8888
    >>> sys/tg_test/1/ampli
    0.0
    >>> sys/tg_test/1/state
    RUNNING
	>>> sys/tg_test/1/nope
    DevFailed[
    DevError[
         desc = Attribute nope is not supported by device sys/tg_test/1
       origin = AttributeProxy::real_constructor()
       reason = API_UnsupportedAttribute
     severity = ERR]
     ]
    ```

---
class: middle

More resources
--------------

### Asyncio overview

- Slides: [vxgmichel.github.io/asyncio-overview](https://vxgmichel.github.io/asyncio-overview)

- Repo: [github.com/vxgmichel/asyncio-overview](https://github.com/vxgmichel/asyncio-overview)


### Previous pytango workshop

ICALECPS 2017
- Slides: [vxgmichel.github.io/icalepcs-workshop](https://vxgmichel.github.io/icalepcs-workshop)

- Repo: [github.com/vxgmichel/icalepcs-workshop](https://github.com/vxgmichel/icalepcs-workshop)

---
class: middle
## New features being considered

* Python logging as standard sends to TANGO Logging Service

```python

class PowerSupply(Device):

    @command
    def calibrate(self):
        self._logger.info('Calibrating...')
        sleep(0.1)

```

* User could add handlers for other targets, e.g., syslog or Elastic

---
class: middle

New features being considered
-----------------------------

* Support forwarded attributes with `DeviceTestContext`

* faketango `Device` for basic unit testing:

```python
import mock
from tango import DevState
from tango.test_utils import DeviceTestContext
from tango.test_utils import faketango

from powersupply.powersupply import PowerSupply

@mock.patch('tango.server.Device', faketango.Device)
def test_init():
    """Test device goes into STANDBY when initialised"""
    DUT = PowerSupply(properties={})
    DUT.Init()
    assert DUT.get_state() == DevState.STANDBY
```

---
name: fandango
layout: true
class: center, middle

---

Fandango - a Swiss army knife for tango
=======================================
ICALEPCS 2019 - New York
[Sergi Rubio Manrique](https://github.com/sergirubio)ICALEPCS 2019 - New York

ICALEPCS 2019 - New York

---
name: whatis
class: middle
layout: true

What is Fandango?
=================

---
class: middle

* a Python library:  pip install fandango

* and a shell script: fandango read_attribute test/dyn/1/t

* https://github.com/tango-controls/fandango

* uses PyTango and DatabaseDS and Starter Device Servers

---
class: middle

It originated from 2 motivations:

* provide a library with utilities/templates for PyTango devices at ALBA

* the desire to get completely rid of Java applications (Jive and Astor)

---
class: middle

It provides many features:

* the origin, functional programming for tango (fun4tango)

* features from Java clients (Jive, Astor)

* utilities for python devices (Logging, Threading, Workers)

* includes methods for functional programming

* enables middle-layer devices (DynamicDS, SimulatorDS, CopyCatDS)

---
name: empty2
layout: true
class: middle

---

fandango submodules
===================

* functional: functional programming, data format conversions,
    caseless regular expressions
* tango : tango api helper methods, search/modify using regular expressions
* dynamic : dynamic attributes, online python code evaluation
* server : Astor-like python API
* device : some templates for Tango device servers
* interface: device server inheritance
* db: MySQL access
* dicts,arrays: advanced containers, sorted/caseless list/dictionaries,
    .csv parsing
* log: logging
* objects: object templates, singletones, structs
* threads: serialized hardware access, multiprocessing
* linos: accessing the operative system from device servers
* web: html parsing
* qt: some custom Qt classes, including worker-like threads.


---

fandango.tango submodules
=========================

* command: asynchronous execution of tango commands on a background thread
* eval/tangoeval: evaluation of formulas using tango attribute values
* dynattr: dynamic typing of attributes, used to override operators on demand
* export: import/export tango attributes/devices/properties on json/pickle formats
* search: methods to search devices/attributes in the tango database or a running control system
* methods: miscellaneous methods to access Tango devices and attributes

---
title: vs
class: middle
layout: true

fandango vs PyTango
===================
---

PyTango is a binding of TANGO C++, thus bringing the same functionality and 
mimicking the same methods and arguments available on C++.

The PyTango High Level API provides a pythonic API for developing
TANGO device servers and clients in Python 3.

fandango instead, extends the API adding some features only available on Java
clients like Jive and Astor, the  default management UI applications of TANGO.

---

Adding a new device with *PyTango* (mimics the C++ API):

```python
add_device(self, dev_info) -> None

        Add a device to the database. The device name, server and class
        are specified in the DbDevInfo structure

        Example :
            dev_info = DbDevInfo()
            dev_info.name = 'my/own/device'
            dev_info._class = 'MyDevice'
            dev_info.server = 'MyServer/test'
            db.add_device(dev_info)

    Parameters :
        - dev_info : (DbDevInfo) device information
```

---

Adding a new device with *fandango* (mimics the Jive UI form):

```python
fn.tango.add_new_device(server, klass, device)

This methods mimics Jive UI forms:

    server: ExecutableName/Instance
    klass:  DeviceClass
    device: domain/family/member
    
e.g.:
    fandango.tango.add_new_device(
      'MyServer/test','MyDevice','my/own/device')
```
---
title: creating
layout: true
class:middle

fandango.tango: creating and launching devices
----------------------------------------------

---

fandango provides Astor python API, providing the same functionality than astor tool.

fandango can be used in python:
```python
import fandango as fn

fn.tango.add_new_device('DynamicDS/1','DynamicDS','test/dyn/1')
astor = fn.Astor()
host = fn.linos.MyMachine().hostname
astor.start_servers('DynamicDS/1',host=host)
astor.set_server_level('DynamicDS/1',level=3,host=host)
```

---

.center[![vacca](images/jive_add_device.png)]

---

methods from fandango can  also be launched linux shell:

```bash
$: fandango add_new_device DynamicDS/1 DynamicDS test/dyn/1

$: fandango put_device_property test/dyn/1 DynamicAttributes "T=t%10"

$: tango_servers $HOSTNAME start DynamicDS/1
```

---

```bash

tango-cs@tangobox:~$ fandango find_devices "*hdb*es*"

dserver/hdb++es-srv/1

tango-cs@tangobox:~$ tango_servers start $(fandango find_devices "*hdb*es*")

start of ['dserver/hdb++es-srv/1'] at *
Loading dserver/hdb++es-srv/1 devices

Starting : ['hdb++es-srv/1']
--------------------------------------------------------------------------------
/home/tango-cs/.local/bin/tango_servers start dserver/hdb++es-srv/1: Done

tango-cs@tangobox:~$ 

```

---
class: middle
layout: true
fandango.tango: searching in the database
-----------------------------------------

---

```python

fandango.find_devices('bo01/vc/*')

fandango.find_attributes('sr12*/*plc*')

fandango.get_matching_device_properties('sr12/vc/eps-plc-01','dynamic*')

```

---


```bash
$ fandango -l find_devices "bl00/*"

bl00/ct/alarms
bl00/ct/ccdalarms-01
bl00/ct/eps-plc-01
bl00/ct/eps-plc-01-mbus
bl00/door/01
bl00/door/02
bl00/door/03
bl00/eh/ccg-fcv-01
bl00/eh/diset-01-ccd
bl00/eh/diset-01-iba
bl00/eh/diset-02-ccd
bl00/eh/diset-02-iba
bl00/eh/fcv-01
bl00/eh/ip-diset-01
bl00/eh/ip-diset-02
bl00/eh/ip-ip100-01
```

---
layout: true
Import/Export Device servers from TANGO Db
------------------------------------------

---

.center[![vacca](images/vacca_tree.png)]

---

Exporting/Importing devices and properties declaration allows to easily
create/move hundreds of devices with a few commands:

```bash

$ tango2json --commands --properties --attributes ../bl00.json "(bl00|fe00)*"

Exporting 58 devices to ../bl00.json

$ ls -lah bl00.json 
-rw-r--r-- 1 tango-cs tango-cs 1,4M paź  5 17:12 bl00.json

```

---

```python
import fandango as fn

jj = fn.json2dict('/home/tango-cs/src/bl00.json')

[fn.tango.import_device_from_dict(d) for d in jj.values()]
```

---

```
tango-cs@tangobox:~/src$ DynamicDS bl09_as_00

Launching /home/tango-cs/src/fandango.git/fandango/device/DynamicDS bl09_as_00

screen -dm -S DynamicDS-bl09_as_00 python 
  /home/tango-cs/src/fandango.git/fandango/device/DynamicDS.py bl09_as_00
```

---

although csv is less popular, tango2csv allows human-readable exports

```
$ tango2csv "(bl00|fe00)*" bl00.csv &

$ less bl00.csv

DynamicDS/bl09_as_00    SimulatorDS     bl00/eh/ip-diset-01
                        Channel P2
                                HV2Status
                                State
                        IonPumpController       BL09/VC/IPCT-02
                        LoadFromFile    /remotenfs/siciliarep/projects/ctmachine/ctvacuum/BL00-09/IonPump_attributes.txt
                        LowRange        1e-12
                        OFFSET  34
                        PollingCycle    3000
                        UseEvents       False
                        _Location       BL09-DI-D
```
---

title: eval
class: middle
layout: true
Evaluating attribute values on runtime
======================================

---

fandango provides two implementations for evaluating python code for attributes:

 * DynamicDS: device template for creating attributes dynamically using properties,
 optimized for reading hundreds of attributes, implementing  caches and hierarchic evaluation.
 
 * TangoEval: generic python evaluator object with Tango syntax parsing, it can
 be used from either devices or clients

---

Declaring Dynamic Attributes on a simulator/composer/processor device:
```python

PLCAttributeValue = DevLong(int(PROPERTY("OFFSET"))+randint(0,10) * choice([0, 1] or [0]))

CCGPressures=DevVarDoubleArray([XAttr('BL00/VC/VGCT-%02d/P%d'%(j,i)) or 1e-12 for j in (3,2,1) for i in (2,1)])

MaxPressure=DevDouble(max(CCGPressures))
```

---

.center[![vacca](images/jive_attributes.png)]

---

Declaring a formula in the PANIC Alarm System (using fandango.TangoEval):
```python

BL00_AIR_PRESSURE:
    BL00/CT/EPS-PLC-01/PAAS_EH01_01_PS1<=4 or BL00/CT/EPS-PLC-01/PAAS_EH01_01_PS2<=4
    
BL09_STATES:
    any([s<0 or str(s) in ('UNKNOWN','FAULT') for s in 
      FIND(BL00/VC/ALL/State)+FIND(BL00/VC/VGCT-0*/State)
      +FIND(BL00/VC/IPCT-0*/State)])
      
BL09_START:
    BL00/VC/Elotech-01/Temperature_Max > 20 

BL00_PRESSURES:
    any([p>8e-07 for p in BL00/VC/ALL/CCGPressures[1:]])
```

---

class: middle
layout: true

Libraries/Projects using fandango
=================================

---

* SimulatorDS Device Server
* CopyCatDS, ComposerDS, PyStateComposer, PyAttributeProcessor, ...
* PANIC Alarm System: [https://github.com/tango-controls/panic]
* PyTangoArchiving
* PyPLC Device Server
* VacuumController Device Servers (Varian, Agilent, MKS, Pfeiffer)
* VACCA User Interface

---
layout: true
name: empty
class: middle
---
class: middle

Fandango and VACCA
------------------

.center[![vacca](images/vacca_tree.png)]

VACCA is an SCADA-like UI build on top of the Taurus (PyQt) library with the purpose
of managing all TANGO related services (Archiving, Alarms, TANGO Db, Hosts) from a single
application.

---
class: middle

Plenty of useful methods:

```python
$ fandango --list

...
fandango.tango.methods.check_attribute
fandango.tango.methods.check_attribute_cached
fandango.tango.methods.check_attribute_events
fandango.tango.methods.check_device
fandango.tango.methods.check_device_cached
fandango.tango.methods.check_device_events
fandango.tango.methods.check_device_list
fandango.tango.methods.check_host
fandango.tango.methods.check_property_extensions
fandango.tango.methods.check_starter
fandango.tango.methods.delete_device
fandango.tango.methods.device_command
fandango.tango.methods.get_alias_dict
fandango.tango.methods.get_alias_for_device
fandango.tango.methods.get_attr_name
fandango.tango.methods.get_attribute_config
fandango.tango.methods.get_attribute_events
...
```

---

Fandango documentation
----------------------

https://pythonhosted.org/fandango

.center[![docs](images/fandango_docs.png)]

---

What is missing?
----------------

The most requested feature:

* PyTango 3

Which is currently blocked by:

* Testing and CI

Two ports to python 3 actually exist (one by me and another from S2Innovation),
but none of them has been yet put in production.

---

layout: true

Deploying taurus-test docker
----------------------------

Reproducing examples with taurus docker (also AWS available)

```bash
https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-repository

sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker your-user
docker run -id --name=taurus-stretch -h taurus-test -e DISPLAY=$DISPLAY -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix cpascual/taurus-test:debian-stretch
docker exec -it taurus-test bash
 
root@taurus-test:~# fandango add_new_device Starter/$HOSTNAME Starter tango/admin/$HOSTNAME
None
root@taurus-test:~# fandango put_device_property tango/admin/$HOSTNAME StartDSPath $(fandango findModule fandango)/devices
StartDSPath /root/fandango/devices
root@taurus-test:~# /usr/lib/tango/Starter taurus-test &
```
