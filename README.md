# PY65816

A 65816 simulation package running on top of [py65](https://github.com/mnaberez/py65).

# Features

* Simulate the W65C816
* Open a separate debug window with a partial set of py65 commands available in realtime
* Interrupt support
    * 65C22 VIA shift register
    * 65C51 ACIA receiver providing "sector" access to simulated storage

# Development

I began developing these as separate enhancements to py65.  You can get some background and use/testing information on each at:
* [65816](https://github.com/tmr4/py65_65816)
* [Debug Window](https://github.com/tmr4/py65_debug_window)
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
-w, --debug                       : Open debug window
-v, --via <address>               : Add a VIA at address
-a, --acia "<address> <filename>" : Add an ACIA at address with filename for block access
````

The py65816 monitor inherits from the py65 monitor so most monitor functions should be the same though I haven't tested many of them.  Mike Naberezny has provided online [documentation](https://py65.readthedocs.io/en/latest/).  The debug window provides a slightly enhanced subset of these commands (type `help` or `h` in the debug window).

# Status
1. About 98% of the code for the new 65C816 device is covered by unit tests and the device has passed them all.  Some known issues/limitations for the 65816 simulation:
    * I use nose2 to evaluate test coverage.  View current unit test coverage with `nose2 --with-coverage` or `nose2 --with-coverage --coverage-report html` for a detailed html report.
    * Extra cycle counts haven't been tested for any new to 65816 opcodes nor direct page wrapping.
    * New 65816 instructions have generally not been tested in emulation mode.
    * Move block instructions haven't been tested in native 8-bit or emulation modes.
    * FIXED: ADC and SBC in decimal mode are likely invalid in 16 bit.
        * Addition and subtraction tested in decimal mode with valid BCD values and for C, Z, and N flags.  Need more unit tests for these, but they have passed Bruce Clark's 8-bit [Decimal Mode Tests](http://6502.org/tutorials/decimal_mode.html#B) and my 16-bit tests based on his formulas (I don't have independent 16-bit tests).  The overflow flag is calculated but I haven't tested whether the value is correct (the 16-bit tests take days to run on my fastest computer).  I have not tested non-valid BCD values.
    * FIXED: Page and bank wrapping needs tested.  Don't count on these being the same as hardware right now.
    * FIXED: Some instructions operating in mixed register modes haven't been fully tested.  For example, TAY, TAX, TXA, TYA when one register is 8-bit and the other is 16-bit.
    * FIXED: PEA and companion instructions haven't been tested.  At this point, assume they don't work properly.
    * VERIFIED w/ [W65C265SXB](https://wdc65xx.com/Single-Board-Computers/w65c265sxb/), a handy development board for 65816 testing: Need to verify consistency of some instructions with hardware.  For example, in native mode I've modeled PLP and RTI as affecting register values if the m and x flags change.  Also I do not change register modes/values when XCE is called when the processor is already in the desired mode.
2. Interrupt handling is very limited, mainly just enough for my own requirements.  But it isn't hard to add other capabilities.  The main consideration is the source of the interrupt trigger.  For example, in my build I use the 65C22 shift register to capture a byte sent from a keyboard controller.  When the shift register receives a complete byte it requests an interrupt from the 6502.  I've modeled the shift register here in a similar way.  It will trigger an interrupt when a keystroke is available.
3. See [Debug Window](https://github.com/tmr4/py65_debug_window) for some of its limitations.

