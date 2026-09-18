#!/usr/bin/env bash
set -euo pipefail
version=0.19.0
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) target=x86_64-unknown-linux-gnu ;;
  Darwin-arm64) target=aarch64-apple-darwin ;;
  *) echo "Install Weaver v$version manually for your platform" >&2; exit 1 ;;
esac
mkdir -p .tools
curl --fail --location --retry 3 "https://github.com/open-telemetry/weaver/releases/download/v$version/weaver-$target.tar.xz" -o .tools/weaver.tar.xz
tar -xf .tools/weaver.tar.xz -C .tools
cp ".tools/weaver-$target/weaver" .tools/weaver
.tools/weaver --version
