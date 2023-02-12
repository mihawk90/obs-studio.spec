#!/bin/sh

spec=./obs-studio.spec
mver=$(cat $spec | grep Version\: | cut -d" " -f9)
rver=$(cat $spec | grep Release\: | cut -d" " -f9 | sed -e 's/%{?dist}//')

if [ "$1" == "qt" ]; then
	rpmdev-bumpspec -c "Rebuild for new Qt5" $spec
#	git diff $spec
	git add $spec
	git commit -m "Rebuild for new Qt5"
	git tag "v$mver-$rver"
	git show HEAD
	exit
fi

pushd obs-studio
git checkout master
git pull
obsVer=$(git tag --list --sort=taggerdate | tail -n1)
git checkout $obsVer
git submodule update --init --recursive
git submodule status
popd

# update commits in spec file
sed --in-place "s/Version:.*/Version:        $obsVer/" $spec
sed --in-place "s/Release:.*/Release:        11%{?dist}/" $spec

if [ "$1" == "cef" ]; then
	sed --in-place "s/%global version_cef .*/%global version_cef $2/" $spec
fi

sed --in-place "s/%changelog/%changelog\n\* $(date +'%a %b %d %Y') Tarulia <mihawk.90+git@googlemail.com> - $obsVer-11\n- Update to $obsVer\n/" $spec

git diff $spec

