#!/bin/bash

if pipenv >/dev/null 2>&1; then
    echo -e "\033[32m\n 新月杀控制面板启动中 ... \n\033[0m"
else
    echo "\033[33m\n 未找到pipenv模块,请先安装 Python 3.11并安装pipenv\n\033[0m"
    exit 1
fi

if pipenv graph > /dev/null 2>&1; then
	pipenv run python ./app.py
else
    echo -e "\033[34m\n 检测到未初始化环境\n\033[0m"
    echo -e "\033[32m\n 正在初始化 ... \n\033[0m"
	pipenv install
    echo -e "\033[32m\n 初始化环境完毕 ... \n\033[0m"
    pipenv run python ./app.py
fi