# PY65816

A 65816 simulation package running on top of [py65](https://github.com/mnaberez/py65).

# Use

Clone, then install locally with `pip install -e .`

Run similarly to py65mon.  For example, get help with `py65816mon -h`.

````
py65816mon -- interact with a simulated 65816-based system

Usage: py65816mon [options]

Options:
-h, --help             : Show this message
-d, --debug            : Toggle debug window
-m, --mpu <device>     : Choose which MPU device (default is 6502)
-l, --load <file>      : Load a file at address 0
-r, --rom <file>       : Load a rom at the top of address space and reset into it
-g, --goto <address>   : Perform a goto command after loading any files
-i, --input <address>  : define location of getc (default $f004)
-o, --output <address> : define location of putc (default $f001)
````

# Status
1. About 97% of the code for the new 65C816 device is covered by unit tests and the device has passed them all.  Some known issues/limitations:
    * Extra cycle counts haven't been considered for any new to 65816 opcodes.
    * ADC and SBC in decimal mode are likely invalid in 16 bit.
    * Page and bank wrapping needs tested.
    * Some instructions operating in mixed register modes haven't been tested.
    * PEA and companion instructions haven't been tested.  At this point, assume they don't work properly.
    * Move block instructions haven't been tested in 8-bit mode.
    * New 65816 instructions have generally not been tested in emulation mode.

View unit test coverage with `nose2 --with-coverage` or `nose2 --with-coverage --coverage-report html` for an html report.
