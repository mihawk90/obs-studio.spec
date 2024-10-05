#!/bin/sh

spec=./obs-studio.spec

pushd obs-studio
git reset --hard
git checkout master
git pull
obsVer=$(git tag --list --sort=taggerdate | tail -n1)
git checkout $obsVer
git submodule update --init --recursive
git submodule status
popd

obsVer=$(echo "$obsVer" | sed "s/-/~/")
# bumpspec writes both the Version and Changelog automatically
rpmdev-bumpspec -n $obsVer -c "Update to $obsVer" $spec
# bumpspec always resets to 1 for -n, but we still want to use 11
sed --in-place "s/Release:.*/Release:        11%{?dist}/" $spec

if [ "$1" == "cef" ]; then
	sed --in-place "s/%global version_cef .*/%global version_cef $2/" $spec
fi

git add $spec
git diff --staged

