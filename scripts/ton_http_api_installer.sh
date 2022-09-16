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
service_name=""
extend_path="from sys import path; path.append('/usr/src/ton-http-api/');"
import_mypylib="from mypylib.mypylib import *;"

pyton_executable_path="/usr/bin/python3 ton-http-api/pyTON"
liteserver_config_path="/usr/bin/ton/global.config.json"
libtonlibjson_path="/usr/bin/ton/tonlib/libtonlibjson.so"
mkdir ~/keystore
touch ~/keystore/keystore.ks
ton_config="--liteserver-config ${liteserver_config_path} --cdll-path ${libtonlibjson_path} --parallel-requests-per-liteserver 100 --tonlib-keystore ~/keystore/keystore.ks"
server_config="--host $(hostname -I) --port 8073"

arg_name="name='ton-http-api'"
arg_user="user='${user}'"
arg_workdir="workdir='/usr/src/ton-http-api'"
arg_start="start='${pyton_executable_path} ${ton_config}'"

systemd_arguments="${arg_name}, ${arg_user}, ${arg_workdir}, ${arg_start}"
systemd_call="Add2Systemd(${systemd_arguments})"

cmd="${extend_path}${import_mypylib}"
mkdir /usr/bin/ton/keystore/ton-keystore
python3 -c "${cmd}"
systemctl restart ton-http-api

echo -e "${COLOR}[3/3]${ENDC} ton-http-api installation complete"
exit 0
