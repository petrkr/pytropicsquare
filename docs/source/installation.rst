Installation
============

PyTropicSquare supports both CPython and MicroPython environments.

CPython
--------

Install from source in a virtual environment::

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .

MicroPython / ESP32
-------------------

Two installation paths are supported on ESP32.

Option 1: Install from a release with ``mip``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connect the board to Wi-Fi and install from a published release asset::

   from network import WLAN

   wlan = WLAN()
   wlan.active(True)
   wlan.connect(ssid, psk)

   import mip
   mip.install("https://github.com/petrkr/pytropicsquare/releases/download/<release-tag>/pytropicsquare-<version>-mip.json")

Example for release ``v0.1.0``::

   import mip
   mip.install("https://github.com/petrkr/pytropicsquare/releases/download/v0.1.0/pytropicsquare-0.1.0-mip.json")

Option 2: Upload from a source checkout with ``mpremote``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upload the library directory directly to the board::

   mpremote cp -r tropicsquare :

To run the ESP32 quickstart example::

   mpremote cp examples/esp32_quickstart.py :main.py
   mpremote reset

See :doc:`examples` and ``examples/esp32_quickstart.py`` for direct SPI usage on ESP32.
