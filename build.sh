#!/bin/bash

build() {
    # 檢查是否已安裝 wheel
    if ! pip show wheel &> /dev/null; then
        echo -e "\x1B[1;31mwheel 未安裝！\x1B[m"
        read -p "是否要使用 pip 安裝 wheel？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "\x1B[1;33m正在安裝 wheel...\x1B[m"
            pip install wheel
            if [ $? -eq 0 ]; then
                echo -e "\x1B[1;32mwheel 安裝成功！\x1B[m"
            else
                echo -e "\x1B[1;31mwheel 安裝失敗！\x1B[m"
                return 1
            fi
        else
            echo -e "\x1B[1;31m取消安裝，無法繼續執行建置流程。\x1B[m"
            return 1
        fi
    fi

    echo -e "\x1B[1;33mStart Building...\x1B[m"
    python setup.py sdist bdist_wheel
}

test_pypi() {
    if [[ -z $1 || $1 -ne 0 ]]; then
        build
    fi
    echo -e "\x1B[1;33mUpload to test.pypi...\x1B[m"
    twine upload --repository testpypi --skip-existing dist/*
}

pypi() {
    if [[ -z $1 || $1 -ne 0 ]]; then
        build
    fi
    echo -e "\x1B[1;33mUpload to pypi...\x1B[m"
    twine upload  --skip-existing dist/*
}

all() {
    build
    test_pypi 0
    pypi 0
}

items=(
    "All"
    "Test-PyPi"
    "PyPi"
)

# 定義 COLUMNS 讓選單只有一欄
COLUMNS=1

# 檢查是否已安裝 twine
if ! command -v twine &> /dev/null; then
    echo -e "\x1B[1;31mtwine 未安裝！\x1B[m"
    read -p "是否要使用 brew 安裝 twine？ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "\x1B[1;33m正在安裝 twine...\x1B[m"
        brew install twine
        if [ $? -eq 0 ]; then
            echo -e "\x1B[1;32mtwine 安裝成功！\x1B[m"
        else
            echo -e "\x1B[1;31mtwine 安裝失敗！\x1B[m"
            exit 1
        fi
    else
        echo -e "\x1B[1;31m取消安裝，無法繼續執行建置流程。\x1B[m"
        exit 1
    fi
fi

PS3="Build for what? "
while true; do
    select item in "${items[@]}" Quit
    do
        case $REPLY in
            1) all; break 2;;
            2) test_pypi; break 2;;
            3) pypi; break 2;;
            $((${#items[@]}+1))) break 2;;
            *) echo "Unknown choice $REPLY"; break;
        esac
    done
done
