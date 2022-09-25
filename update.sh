#!/bin/sh

pushd obs-studio
git checkout master
git pull
obsVer=$(git tag --list --sort=taggerdate | tail -n1)
git checkout $obsVer
git submodule update --init --recursive
git submodule status
popd

# update commits in spec file
sed --in-place "s/Version:.*/Version:        $obsVer/" ./obs-studio.spec
sed --in-place "s/Release:.*/Release:        11%{?dist}/" ./obs-studio.spec

if [ "$1" == "cef" ]; then
	sed --in-place "s/%global version_cef .*/%global version_cef $2/" ./obs-studio.spec
fi

sed --in-place "s/%changelog/%changelog\n\* $(date +'%a %b %d %Y') Tarulia <mihawk.90+git@googlemail.com> - $obsVer-11\n- Update to $obsVer\n/" obs-studio.spec

git diff obs-studio.spec

