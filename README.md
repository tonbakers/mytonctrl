
# Cli wrapper for "mytonctrl"  
  
To install this tool you need to apply action as described above
1. Run following command on your machine with keyword `-m full` or `-m lite`:
```sh  
wget https://github.com/tonbakers/mytonctrl/blob/master/scripts/install.sh && sudo bash install.sh -m full
```
After installation ends you will see the next message:
```bash
 . . .
[4/4] Mytonctrl installation completed
```
2. After installation successfully ends type in command line the following:
```bash  
Usage: manage.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-config  Generates config for local validator.
  get            Get network settings.
  mc             Move coins to specified account/wallet.
  set            Set network settings.
  status         Get wallet status information.
  update         Update "mytonctrl" to actual version
  upgrade        Upgrade TON sources to the latest version.
  vote           Vote offer.
  wallets-list   Wallets list of your account.
```
To get more information about **cli** commands, you need to type a command and flag `--help` after:
```bash
# Example:
> python manage.py status --help  
Usage: manage.py status [OPTIONS] [STATUS_TYPE]  
  
 Get wallet status information.  
Options:  
 --help  Show this message and exit.  
```
