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

liteserver_config_path="/usr/bin/ton/global.config.json"
libtonlibjson_path="/usr/bin/ton/tonlib/libtonlibjson.so"

server_config="--host $(hostname -I) --port 8073"
ton_config="--liteserver-config ${liteserver_config_path} --cdll-path ${libtonlibjson_path} --parallel-requests-per-liteserver 100 --tonlib-keystore ~/keystore/keystore.ks"
pyton_executable_path="/usr/bin/python3 ton-http-api/pyTON"

keystore_contents="$(cat ~/keystore/keystore.ks)"
rm -rf ~/keystore
mkdir ~/keystore
echo "${keystore_contents}" >~/keystore/keystore.ks

cat > /etc/systemd/system/ton-http-api.service <<- EOM
[Unit]
Description=ton-http-api service. Created by https://toncenter.com/
After=network.target
StartLimitIntervalSec=0
StartLimitBurst=5
StartLimitIntervalSec=10

[Service]
Type=simple
Restart=always
RestartSec=30
ExecStart=${pyton_executable_path} ${server_config} ${ton_config}
ExecStopPost=/bin/echo "Stopping ton-http-api. This operation can take few minutes."
User=${user}
LimitNOFILE=infinity
LimitNPROC=infinity
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
EOM

systemctl restart ton-http-api

echo -e "${COLOR}[3/3]${ENDC} ton-http-api installation complete"
exit 0
