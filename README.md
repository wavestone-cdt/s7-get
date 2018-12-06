# s7-get

Python scripts that allow to send read/write **s7communication** requests to **Siemens** S7 PLCs.

The different arguments can be given directly in command line.

Here is how to use it: *s7get.py -a `address` -m `mode` -n `number` -d `data` ip_address*

>    * -a    Address from which data will be read/written
>    * -m    [r|w] Chosen mode of the program, whether you want to read or write on the PLC
>    * -n    Number of data you want to read/write
>    * -d    Data in binary to write (e.g. 1001)

S7getDB is the same tool but allows to write on the DB section instead of digital outputs.
The db number can be specified with the -db option.

This tool is based on Snap7 library, as well as the Python wrapper.
Install docs can be found here : http://python-snap7.readthedocs.org/en/latest/installation.html
