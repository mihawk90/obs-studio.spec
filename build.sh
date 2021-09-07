#!/bin/sh

### preparation

spec=./obs-studio.spec

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
	if [[ $(cat "./obs-secrets" | grep TWITCH_CLIENTID) ]]; then
		sed --in-place "s/-DTWITCH_CLIENTID='.*'/-DTWITCH_CLIENTID='$(cat "./obs-secrets"| grep TWITCH_CLIENTID | cut -d' ' -f2)'/" $spec
		sed --in-place "s/-DTWITCH_HASH='.*'/-DTWITCH_HASH='$(cat "./obs-secrets"| grep TWITCH_HASH | cut -d' ' -f2)'/" $spec
	fi

	if [[ $(cat "./obs-secrets" | grep RESTREAM_CLIENTID) ]]; then
		sed --in-place "s/-DRESTREAM_CLIENTID='.*'/-DRESTREAM_CLIENTID='$(cat "./obs-secrets"| grep RESTREAM_CLIENTID | cut -d' ' -f2)'/" $spec
		sed --in-place "s/-DRESTREAM_HASH='.*'/-DRESTREAM_HASH='$(cat "./obs-secrets"| grep RESTREAM_HASH | cut -d' ' -f2)'/" $spec
	fi

	#TODO: YouTube secrets
	if [[ $(cat "./obs-secrets" | grep YOUTUBE_CLIENTID) ]]; then
		sed --in-place "s/-DYOUTUBE_CLIENTID='.*'/-DYOUTUBE_CLIENTID='$(cat "./obs-secrets"| grep -w YOUTUBE_CLIENTID | cut -d' ' -f2)'/" $spec
		sed --in-place "s/-DYOUTUBE_CLIENTID_HASH='.*'/-DYOUTUBE_CLIENTID_HASH='$(cat "./obs-secrets"| grep -w YOUTUBE_CLIENTID_HASH | cut -d' ' -f2)'/" $spec
		sed --in-place "s/-DYOUTUBE_SECRET='.*'/-DYOUTUBE_SECRET='$(cat "./obs-secrets"| grep -w YOUTUBE_SECRET | cut -d' ' -f2)'/" $spec
		sed --in-place "s/-DYOUTUBE_SECRET_HASH='.*'/-DYOUTUBE_SECRET_HASH='$(cat "./obs-secrets"| grep -w YOUTUBE_SECRET_HASH | cut -d' ' -f2)'/" $spec
	fi

fi

### build phase

spectool -g $spec --directory ./f_downloads
mock -r fedora-$frel-x86_64-rpmfusion_free --sources=./f_downloads --spec=$spec

mkdir -p f_upload && pushd ./f_upload
cp /var/lib/mock/fedora-$frel-x86_64/result/obs-studio-*$mver-$rver.fc$frel.*.rpm .
sha512sum obs-studio-$mver-$rver.fc$frel.x86_64.rpm > obs-studio-$mver-$rver.fc$frel.x86_64.rpm.sha512
sha512sum obs-studio-libs-$mver-$rver.fc$frel.x86_64.rpm > obs-studio-libs-$mver-$rver.fc$frel.x86_64.rpm.sha512
echo "Copied RPM to current directory. Enter sudo-password to install using DNF. Press Ctrl-c to cancel installation."
sudo dnf install obs-studio-$mver-$rver.fc$frel.x86_64.rpm obs-studio-libs-$mver-$rver.fc$frel.x86_64.rpm
popd

### clean up client secrets
# can always do this with the .* quantifier

sed --in-place "s/-DTWITCH_CLIENTID='.*'/-DTWITCH_CLIENTID=''/" $spec
sed --in-place "s/-DTWITCH_HASH='.*'/-DTWITCH_HASH=''/" $spec

sed --in-place "s/-DRESTREAM_CLIENTID='.*'/-DRESTREAM_CLIENTID=''/" $spec
sed --in-place "s/-DRESTREAM_HASH='.*'/-DRESTREAM_HASH=''/" $spec

sed --in-place "s/-DYOUTUBE_CLIENTID='.*'/-DYOUTUBE_CLIENTID=''/" $spec
sed --in-place "s/-DYOUTUBE_CLIENTID_HASH='.*'/-DYOUTUBE_CLIENTID_HASH=''/" $spec
sed --in-place "s/-DYOUTUBE_SECRET='.*'/-DYOUTUBE_SECRET=''/" $spec
sed --in-place "s/-DYOUTUBE_SECRET_HASH='.*'/-DYOUTUBE_SECRET_HASH=''/" $spec

echo "All done!"

