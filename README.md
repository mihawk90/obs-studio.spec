# What?

A Spec file for building an RPM package of [OBS Studio](https://obsproject.com) on Fedora. This could be adapted to build on RHEL and derivatives as well, but has not been tested. SUSE likewise has also not been tested.

I also provide precompiled packages on the [release page](https://github.com/mihawk90/obs-studio.spec/releases) and via a PackageCloud Repository.

# Why?

Due to packaging constraints the RPM Fusion package up until Fedora 35 and the Fedora package since then were/are missing some components, most notably [obs-browser](https://github.com/obsproject/obs-browser) - which is used for Browser Sources, Custom Browser Docks, as well as service integrations (Twitch login). So I set out to build my own package to get as close to the official Ubuntu PPA as possible.

Note: Currently I don't build the AJA module because I don't have one of these cards and it was a bit of a PITA to build everytime. If anyone has need, please open an issue and I'll see to get it back in.

## Patches

Occasionally I may include patches from upstream PRs. If you happen to be using or testing the patched changes, please provide any feedback on the corresponding PR.

Current included patches:

* none

If you would like a PR to be included for testing or actual usage, please open an issue or ping me in `#linux-support` on the OBS Discord.

# Installation

> [!IMPORTANT]
> This package requires RPM Fusion to be enabled on your system. Check [their guide](https://rpmfusion.org/Configuration) on how to enable it.

## PackageCloud Repository

Due to the way the package is built, it can't currently be hosted on COPR, so I'm providing a [PackageCloud repo](https://packagecloud.io/tarulia/obs-studio) instead. The PackageCloud repo install script is kind of a PITA and didn't work for me last time I checked, so I included the `.repo` file here instead.

```sh
$ dnf config-manager addrepo --from-repofile=https://raw.githubusercontent.com/mihawk90/obs-studio.spec/refs/heads/f33/tarulia_obs-studio.repo
# if you have not yet installed obs-studio at all
$ dnf install obs-studio
# if you have obs-studio installed from Fedora repos
$ dnf update obs-studio
```

The `.repo` file also contains a repository for pre-release (Beta/RC) versions, disabled by default. You can enable it permanently or per transaction:
```sh
# permanent
$ dnf config-manager setopt tarulia_obs-studio-pre.enabled=1
# per transaction
$ dnf <install/update> obs-studio --enable-repo=tarulia_obs-studio-pre
```

## Manual

1. Go to the [release page](https://github.com/mihawk90/obs-studio.spec/releases)
2. On the Release under Assets (might need to click "Show all XX assets") download `obs-studio-<version>-11.fc<fedora-release>.x86_64.rpm`, and (optionally) `obs-studio-<version>-11.fc<fedora-release>.sha512`
3. In a terminal:
    ```sh
    $ cd <whereever you put the download>
    # optional:
    $ sha512sum -c obs-studio-<version>-11.fc<fedora-release>.sha512
    # if it comes back OK (you can ignore FAILED on the -devel file if you didn't download it)
    $ dnf install ./obs-studio-<version>-11.fc<fedora-release>.x86_64.rpm
    ```

# Disclaimer

This repository and OBS build is not related to or endorsed by the OBS Project. I do this in my free time for my own use.

# Thanks

Most of the groundwork for packaging was done by [RPM Fusion](https://admin.rpmfusion.org/pkgdb/package/free/obs-studio/) and I simply added what I needed back then. I've long since diverted from their spec (not least of which because the RPM Fusion package was obsoleted in favor of the [Fedora package](https://packages.fedoraproject.org/pkgs/obs-studio/obs-studio/)), but large parts of the spec are still based on their work.

Thanks also goes to [Conan-Kudo](https://github.com/Conan-Kudo) who put an immense amount of work into making OBS Studio available in Fedora, and also maintaing some of the dependency packages to make this possible.

And last but not least, the OBS Project team for creating OBS Studio in the first place and being patient with me whenever I nag them with compiler issues 👀
