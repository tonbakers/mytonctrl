#!/usr/bin/env bash

set -e

if [ "$(id -u)" != "0" ]; then
	echo "Please run script as root"
	exit 1
fi

while getopts u: flag
do
	case "${flag}" in
		u) user=${OPTARG};;
	esac
done

echo -e "${COLOR}[1/3]${ENDC} Installing ton-http-api"
cd /usr/src
rm -rf ton-http-api

git clone https://github.com/toncenter/ton-http-api.git

cd /usr/src/ton-http-api/ton-http-api
python3 setup.py install


echo -e "${COLOR}[2/3]${ENDC} Add to startup"
cmd="from sys import path; path.append('/usr/src/mytonctrl/');  from mypylib.mypylib import *; Add2Systemd(name='ton-http-api', user='${user}', workdir='/usr/src/ton-http-api', start='/usr/bin/python3 -m ton_http_api --liteserverconfig /usr/bin/ton/local.config.json --libtonlibjson /usr/bin/ton/tonlib/libtonlibjson.so')"
python3 -c "${cmd}"
systemctl restart ton-http-api

echo -e "${COLOR}[3/3]${ENDC} ton-http-api installation complete"
exit 0
