# nCipher_Logs

Parses the either the named _nfdiag.txt_ or _nfdiag.zip_ log bundle summary file created from the nfdiag tool. 
These files are themselves a parse of several log files compiled into a single file. 
It is this file that is guaranteed to be received by customer support.

`usage: nfdiag.py [-h] [-v] [-a [Days]] [-d] [-s] File

Cross platform nfdiag log parser

positional arguments:
  File                  <nfdiag-file>

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program version
  -a [Days], --archive [Days]
                        Number of archive days to search
  -d, --debug           Debug logging level
  -s, --statistics      Show historical statistics`

###### **What are the benefits of this nfdiag tool**
* Trawling through 60k lines of a 6Mb log file can be tedious to say the least.
* 1-8 second elapsed runtimes
* Outputs colour summary of results [OK] or [NOK] to screen for instant diagnostics
* Strips config files to active directives only
* Applies logic that can be maintained and configured in supplied JSON files
* Full result output to file
* Runtime logging
 
https://github.com/dougalhatesrabbits/nCipher_Logs_Core.git