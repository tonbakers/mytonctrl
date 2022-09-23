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

echo -e "${COLOR}[1/4]${ENDC} Installing ton-http-api"
cd /usr/src
rm -rf ton-http-api

git clone https://github.com/toncenter/ton-http-api.git

cd /usr/src/ton-http-api/ton-http-api
python3 setup.py install


echo -e "${COLOR}[2/4]${ENDC} Add to startup"

liteserver_config_path="/usr/bin/ton/global.config.json"
libtonlibjson_path="/usr/bin/ton/tonlib/libtonlibjson.so"

server_config="--host $(hostname -I) --port 8073"
ton_config="--liteserver-config ${liteserver_config_path} --cdll-path ${libtonlibjson_path} --parallel-requests-per-liteserver 100 --tonlib-keystore ~/keystore"
pyton_executable_path="/usr/bin/python3 ton-http-api/pyTON"
if [-d ~/keystore ]; then
  cp -r ~/keystore /tmp
  rm -rf ~/keystore
  cp -r /tmp/keystore ~
else
  mkdir ~/keystore

cat > /etc/systemd/system/ton-http-api.service <<- EOM
[Unit]
Description=ton-http-api service. Created by https://toncenter.com/ & improved by "tonbakers"
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
systemctl daemon-reload
systemctl restart ton-http-api

echo -e "${COLOR}[3/4]${ENDC} installing docker engine"
if [ -f /usr/bin/docker ]; then
  echo -e "Docker engine already installed"
else
  echo "Installing docker-engine"
  sudo apt update -y
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update -y
  sudo apt install -y docker-ce
fi

echo -e "${COLOR}[4/4]${ENDC} installing docker-compose"
if [ -f /usr/local/bin/docker-compose ]; then
  echo "docker-compose already installed"
else
  echo "Installing docker-compose"
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version && echo "docker-compose command not found! Try to install it by your self."
fi

exit 0
