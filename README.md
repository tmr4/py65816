# PY65816

A 65816 simulation package running on top of [py65](https://github.com/mnaberez/py65).  For more detail on the simulation and it's development see https://github.com/tmr4/py65_65816.

# Features

* Simulate the W65C816
* Open a separate debug window with a partial set of py65 commands available in realtime
* Interrupt support
    * 65C22 VIA shift register
    * 65C51 ACIA receiver providing "sector" access to simulated storage

# Development

I began developing these as separate enhancements to py65.  You can get some background and use/testing information on each at:
    * [65816](https://github.com/tmr4/py65_65816)
    * [Debug Window]((https://github.com/tmr4/py65_debug_window)
    * [Interrupts](https://github.com/tmr4/py65_int)

This repo pulls them all together into a single package separate from py65.

# Monitor Use

Clone, then install locally with `pip install -e .`.  Start the monitor with `py65816mon`.

The monitor is based on py65mon but supports a few extra command-line options.  For a current set, get help with `py65816mon -h`.

````
py65816mon -- interact with a simulated 65816-based system

Usage: py65816mon [options]

Options:
-h, --help                        : Show this message
-m, --mpu <device>                : Choose which MPU device (default is 65816)
-l, --load <file>                 : Load a file at address 0
-r, --rom <file>                  : Load a rom at the top of address space and reset into it
-g, --goto <address>              : Perform a goto command after loading any files
-i, --input <address>             : define location of getc (default $f004)
-o, --output <address>            : define location of putc (default $f001)
-d, --debug                       : Open debug window
-v, --via <address>               : Add a VIA at address
-a, --acia "<address> <filename>" : Add an ACIA at address with filename for block access
````

The py65816 monitor inherits from the py65 monitor so most monitor functions should be the same.  Mike Naberezny has provided online [documentation](https://py65.readthedocs.io/en/latest/).  The debug window provides a a slightly enhanced subset of these commands (type `help` or `h` in the debug window).

# Status
1. About 98% of the code for the new 65C816 device is covered by unit tests and the device has passed them all.  Some known issues/limitations:
    * I use nose2 to evaluate test coverage.  View current unit test coverage with `nose2 --with-coverage` or `nose2 --with-coverage --coverage-report html` for a detailed html report.
    * Extra cycle counts haven't been considered for any new to 65816 opcodes.
    * ADC and SBC in decimal mode are likely invalid in 16 bit.
    * Page and bank wrapping needs tested.  Don't count on these being the same as hardware right now.
    * Some instructions operating in mixed register modes haven't been fully tested.  For example, TAY, TAX, TXA, TYA when one register is 8-bit and the other is 16-bit.
    * FIXED: PEA and companion instructions haven't been tested.  At this point, assume they don't work properly.
    * Move block instructions haven't been tested in 8-bit mode.
    * New 65816 instructions have generally not been tested in emulation mode.
2. Interrupt handling is very limited, mainly just enough for my own requirements.  But it isn't hard to add other capabilities.  The main consideration is the source of the interrupt trigger.  For example, in my build I use the 65C22 shift register to capture a byte sent from a keyboard controller.  When the shift register receives a complete byte it requests an interrupt from the 6502.  I've modeled the shift register here in a similar way.  It will trigger an interrupt when a keystroke is available.
3. See [Debug Window]((https://github.com/tmr4/py65_debug_window) for some of its limitations.

