#!/bin/sh

currentPath="$(realpath $0)"
parentDir=$(dirname "$currentPath")

destinationDir="$HOME/.mozilla/native-messaging-hosts"
[ -d "$destinationDir" ] || mkdir -p "$destinationDir"

sed "s;<<DIR>>;${parentDir};" ./app.manifest.template.json > "${destinationDir}/ytdlp.firefox.extension.app.json"
