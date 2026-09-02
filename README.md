[![License: GPL3](https://img.shields.io/badge/License-GPL3-yellow.svg)](https://opensource.org/licenses/GPL-3.0)


# Mpie Addons repo V2.10

For Kodi 19+

---
## Support

Use the github issue tab

---
## Fixing a dead channel or adding a category

Channels and categories live in [`repo/config/doofree.json`](repo/config/doofree.json),
not in the code. Edit that file and push it. That is the whole procedure: no
version bump, no zip, and viewers do not have to update the addon. Every
installation picks the change up within a few hours, or immediately after a
restart.

The addon prefers its cached copy while that is fresh, then the file above,
then the copy shipped inside the addon. A file that will not parse, declares an
unknown `schema`, or lists no channels and no categories is ignored, so a
mistake falls back to the previous behaviour instead of emptying the menu.
Entries missing a `url` or a `catid` are dropped individually.

## Cutting a release

Only needed when the addon code itself changes.

```
./release.py --bump patch      # 5.4.0 -> 5.4.1, also minor and major
./release.py --version 6.0.0   # set it exactly
./release.py --news "..."      # replace the release note
./release.py --check           # verify what is on disk, change nothing
```

The script reads the version from the addon manifest and makes everything else
follow: it copies the served configuration in as the offline fallback,
regenerates `addons.xml` from the manifests, builds the zips, writes the
checksum, and then verifies its own output. It does not commit or push.

Kodi only sees an update when the manifest version, the version in
`addons.xml`, the checksum of `addons.xml` and the zip filename all agree.
Running `./release.py --check` tells you whether they do.
