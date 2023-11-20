#!/bin/bash

if pipenv >/dev/null 2>&1; then
    echo -e "\033[32m\n 新月杀控制面板启动中 ... \n\033[0m"
else
    echo -e "\033[33m\n 未找到pipenv模块,请先使用 pip install pipenv 安装pipenv\n\033[0m"
    exit 1
fi

echo -e "\033[32m\n 正在同步环境 ... \n\033[0m"
pipenv install
echo -e "\033[32m\n 环境同步完毕 ... \n\033[0m"
pipenv run python ./app.py
