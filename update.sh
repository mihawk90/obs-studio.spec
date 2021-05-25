#!/bin/sh

cd obs-studio
git checkout master
git pull
git checkout 27.0.0-rc6 # $(cat $spec | grep Version\: | cut -d" " -f9)   # git tag -l | tail -n1
git submodule update
git submodule status | tee ../submodules.txt
cd ..

# update commits in spec file
sed --in-place "s/%global commit_vst .*/%global commit_vst $(cat submodules.txt | grep obs-vst | cut -d' ' -f2 )/" obs-studio.spec
sed --in-place "s/%global commit_browser .*/%global commit_browser $(cat submodules.txt | grep obs-browser | cut -d' ' -f2 )/" obs-studio.spec

rm submodules.txt

if [ "$1" == "cef" ]; then
	sed --in-place "s/%global version_cef .*/%global version_cef $2/" obs-studio.spec
fi

sed --in-place "s/%changelog/%changelog\n\* $(date +'%a %b %d %Y') Tarulia <mihawk.90+git@googlemail.com> - Version\n- \n/" obs-studio.spec

git diff obs-studio.spec

