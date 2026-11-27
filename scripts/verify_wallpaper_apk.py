#!/usr/bin/env python3
"""Check the compiled wallpaper contract without a device or test dependencies."""

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import subprocess
import sys


PACKAGE = "com.lumina.wallpaper"
SERVICE = f"{PACKAGE}.service.CosmicWallpaperService"


@dataclass
class Element:
    name: str
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


def xml_tree(dump):
    """Read the element/attribute lines from `aapt dump xmltree`."""
    root = Element("")
    stack = [(-1, root)]
    for line in dump.splitlines():
        if match := re.match(r"^( *)E: (\S+)", line):
            depth, name = match.groups()
            while stack[-1][0] >= len(depth):
                stack.pop()
            node = Element(name)
            stack[-1][1].children.append(node)
            stack.append((len(depth), node))
        elif match := re.match(r"^ *A: ([^(=]+)(?:\([^)]*\))?=(.*)$", line):
            name, value = match.groups()
            stack[-1][1].attributes[name] = value
    require(len(root.children) == 1, "Expected one compiled XML root")
    return root.children[0]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def has_string(node, key, value):
    return node.attributes.get(key, "").split('"')[1:2] == [value]


def only_child(node, name):
    matches = [child for child in node.children if child.name == name]
    require(len(matches) == 1, f"Expected one <{name}> under <{node.name}>")
    return matches[0]


def verify(apk, build_tools):
    def dump(tool, *args):
        result = subprocess.run([build_tools / tool, *args], check=True, capture_output=True, text=True)
        return result.stdout

    permissions = dump("aapt", "dump", "permissions", apk)
    require(not any(line.lstrip().startswith("uses-permission") for line in permissions.splitlines()),
            f"APK requests permissions: {permissions.strip()}")
    manifest = xml_tree(dump("aapt", "dump", "xmltree", apk, "AndroidManifest.xml"))
    service = only_child(only_child(manifest, "application"), "service")
    require(has_string(service, "android:name", SERVICE), "Wrong wallpaper service class in manifest")
    require(service.attributes.get("android:exported") == "(type 0x12)0xffffffff", "Service is not exported")
    require(has_string(service, "android:permission", "android.permission.BIND_WALLPAPER"),
            "Wallpaper service is not protected by BIND_WALLPAPER")
    action = only_child(only_child(service, "intent-filter"), "action")
    require(has_string(action, "android:name", "android.service.wallpaper.WallpaperService"),
            "Missing WallpaperService intent action")
    metadata = only_child(service, "meta-data")
    require(has_string(metadata, "android:name", "android.service.wallpaper"), "Wrong wallpaper metadata key")
    resources = dump("aapt", "dump", "resources", apk)
    resource = re.search(rf"\bspec resource (0x[0-9a-f]+) {re.escape(PACKAGE)}:xml/cosmic_wallpaper:", resources)
    require(resource is not None and metadata.attributes.get("android:resource") == "@" + resource[1],
            "Manifest does not point to the compiled cosmic wallpaper XML")
    wallpaper = xml_tree(dump("aapt", "dump", "xmltree", apk, "res/xml/cosmic_wallpaper.xml"))
    require(wallpaper.name == "wallpaper" and wallpaper.attributes.get("android:description", "").startswith("@0x"),
            "Invalid wallpaper metadata XML")

    dex = dump("dexdump", "-d", apk)
    classes = {
        match[1]: block
        for block in re.split(r"(?m)^Class #\d+", dex)
        if (match := re.search(r"Class descriptor\s*:\s*'(L[^']+;)'", block))
    }
    service_descriptor = "L" + SERVICE.replace(".", "/") + ";"
    require(re.search(r"Superclass\s*:\s*'Landroid/service/wallpaper/WallpaperService;'", classes.get(service_descriptor, "")),
            "APK service class does not extend WallpaperService")
    activity_descriptor = "L" + PACKAGE.replace(".", "/") + "/MainActivity;"
    activity = classes.get(activity_descriptor, "")
    for value in ("setOnClickListener", "openWallpaperPreview", "Landroid/content/ComponentName;",
                  service_descriptor, "android.service.wallpaper.CHANGE_LIVE_WALLPAPER",
                  "android.service.wallpaper.extra.LIVE_WALLPAPER_COMPONENT", "putExtra", "startActivity",
                  "Landroid/content/ActivityNotFoundException;"):
        require(value in activity, f"Missing preview wiring in compiled MainActivity: {value}")
    print("Verified: no requested permissions, protected WallpaperService, compiled metadata, and preview intent wiring.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("build_tools", type=Path)
    args = parser.parse_args()
    try:
        verify(args.apk, args.build_tools)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        message = str(error).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error title=Wallpaper APK validation failed::{message}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
