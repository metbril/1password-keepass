# 1password-keepass

This script converts a tab delimited text file from [1Password](https://1password.com) to a [KeePass](https://keepass.info) or [KeePassX](https://keepassx.org) xml file.

Inspired by the [1password-to-keepassx.py](https://gist.github.com/stromnet/5539aee578b2717178508b75c1fd82e5) gist.

Tested on macOS 10.12.4 Sierra with Python 3.6.1, 1Password 6.7 and KeepassX 0.4.4.

## Usage

Type `python3 1password-keepass.py --help` for more information on how to use the script.

The script only processes 'Login' rows and only parses "generic fields".
