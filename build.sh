#!/bin/bash

build() {
    python setup.py sdist bdist_wheel
}

test_pypi() {
    if [[ -z $1 || $1 -ne 0 ]]; then
        build
    fi
    twine upload --repository testpypi --skip-existing dist/*
}

pypi() {
    if [[ -z $1 || $1 -ne 0 ]]; then
        build
    fi
    twine upload  --skip-existing dist/*
}

all() {
    build
    test_pypi 0
    test_pypi 0
}

items=(
    "All"
    "Test-PyPi"
    "PyPi"
)

# 定義 COLUMNS 讓選單只有一欄
COLUMNS=1

PS3="Build for what? "
while true; do
    select item in "${items[@]}" Quit
    do
        case $REPLY in
            1) all; break 2;;
            2) test_pypi; break 2;;
            3) pypi; brea 2;;
            $((${#items[@]}+1))) break 2;;
            *) echo "Unknown choice $REPLY"; break;
        esac
    done
done
