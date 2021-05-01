#!/bin/sh

### preparation

spec=obs-studio.spec

if [ "$1" == "frel" ] && [ "$2" != "" ]; then
    frel=$2
    echo "Fedora Release version specified. Using $frel."
else
    frel=$(rpm -E %fedora)
    echo "No Fedora Release version specified. Using default $frel."
fi;

# delimited by spaces, every space is a new "field" for cut, hence field 9 for the version/release
mver=$(cat $spec | grep Version\: | cut -d" " -f9)
rver=$(cat $spec | grep Release\: | cut -d" " -f9 | sed -e 's/%{?dist}//')

# insert the client IDs and Hashes from obs-secrets file
if [[ -f "./obs-secrets" ]]; then
	echo "obs-secrets exists"
	if [[ $(cat "./obs-secrets" | grep TWITCH_CLIENT) ]]; then
		sed --in-place "s/-DTWITCH_CLIENTID='.*' -/-DTWITCH_CLIENTID='$(cat obs-secrets| grep TWITCH_CLIENT | cut -d' ' -f2)' -/" obs-studio.spec
		sed --in-place "s/-DTWITCH_HASH='.*'/-DTWITCH_HASH='$(cat obs-secrets| grep TWITCH_HASH | cut -d' ' -f2)'/" obs-studio.spec
	fi

	if [[ $(cat "./obs-secrets" | grep RESTREAM_CLIENT) ]]; then
		sed --in-place "s/-DRESTREAM_CLIENTID='.*' -/-DRESTREAM_CLIENTID='$(cat obs-secrets| grep RESTREAM_CLIENT | cut -d' ' -f2)' -/" obs-studio.spec
		sed --in-place "s/-DRESTREAM_HASH='.*'/-DRESTREAM_HASH='$(cat obs-secrets| grep RESTREAM_HASH | cut -d' ' -f2)'/" obs-studio.spec
	fi
fi

### build phase

spectool -g $spec
rm obs-studio-$mver-$rver.fc$frel.*.rpm
mock -r fedora-$frel-x86_64-rpmfusion_free --sources=. --spec=$spec

cp /var/lib/mock/fedora-$frel-x86_64/result/obs-studio-*$mver-$rver.fc$frel.*.rpm .
echo "Copied RPM to current directory. Enter sudo-password to install using DNF. Press Ctrl-c to cancel installation."
sudo dnf install obs-studio-$mver-$rver.fc$frel.x86_64.rpm obs-studio-libs-$mver-$rver.fc$frel.x86_64.rpm

### clean up

# clean up client secrets, can always do this with the .* quantifier
sed --in-place "s/-DTWITCH_CLIENTID='.*' -/-DTWITCH_CLIENTID='' -/" obs-studio.spec
sed --in-place "s/-DTWITCH_HASH='.*'/-DTWITCH_HASH=''/" obs-studio.spec
sed --in-place "s/-DRESTREAM_CLIENTID='.*' -/-DRESTREAM_CLIENTID='' -/" obs-studio.spec
sed --in-place "s/-DRESTREAM_HASH='.*'/-DRESTREAM_HASH=''/" obs-studio.spec

echo "All done!"

