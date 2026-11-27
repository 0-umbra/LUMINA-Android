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


def resource_id(resources, name):
    match = re.search(rf"\bspec resource (0x[0-9a-f]+) {re.escape(PACKAGE + ':' + name)}:", resources)
    require(match is not None, f"Resource {name} is not packaged")
    return "@" + match[1]


def method_block(class_dump, name):
    declarations = list(re.finditer(r"(?m)^[ \t]+name\s*:\s*'([^']+)'", class_dump))
    for index, declaration in enumerate(declarations):
        if declaration[1] == name:
            end = declarations[index + 1].start() if index + 1 < len(declarations) else len(class_dump)
            return class_dump[declaration.end():end]
    raise ValueError(f"Missing compiled method: {name}")


def require_in_order(block, *tokens):
    offset = 0
    for token in tokens:
        position = block.find(token, offset)
        require(position != -1, f"Missing or out-of-order preview wiring: {token}")
        offset = position + len(token)


def verify(apk, build_tools):
    def dump(tool, *args):
        result = subprocess.run([build_tools / tool, *args], check=True, capture_output=True, text=True)
        return result.stdout

    permissions = dump("aapt", "dump", "permissions", apk)
    require(not any(line.lstrip().startswith("uses-permission") for line in permissions.splitlines()),
            f"APK requests permissions: {permissions.strip()}")
    manifest = xml_tree(dump("aapt", "dump", "xmltree", apk, "AndroidManifest.xml"))
    require(has_string(manifest, "package", PACKAGE), "Wrong APK application ID for preview component")
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
    require(metadata.attributes.get("android:resource") == resource_id(resources, "xml/cosmic_wallpaper"),
            "Manifest does not point to the compiled cosmic wallpaper XML")
    wallpaper = xml_tree(dump("aapt", "dump", "xmltree", apk, "res/xml/cosmic_wallpaper.xml"))
    require(wallpaper.name == "wallpaper", "Invalid wallpaper metadata XML root")
    require(wallpaper.attributes.get("android:description") == resource_id(resources, "string/wallpaper_description"),
            "Wallpaper metadata does not reference the packaged description")

    dex = dump("dexdump", "-d", apk)
    classes = {
        match[1]: block
        for block in re.split(r"(?m)^Class #\d+", dex)
        if (match := re.search(r"Class descriptor\s*:\s*'(L[^']+;)'", block))
    }
    service_descriptor = "L" + SERVICE.replace(".", "/") + ";"
    service_class = classes.get(service_descriptor, "")
    require(re.search(r"Superclass\s*:\s*'Landroid/service/wallpaper/WallpaperService;'", service_class),
            "APK service class does not extend WallpaperService")
    require("CosmicEngine" in method_block(service_class, "onCreateEngine"), "Service does not create its wallpaper engine")
    activity_descriptor = "L" + PACKAGE.replace(".", "/") + "/MainActivity;"
    activity = classes.get(activity_descriptor, "")
    require("setOnClickListener" in activity and "openWallpaperPreview" in activity, "Preview button is not wired")
    preview = method_block(activity, "openWallpaperPreview")
    require(re.search(r"const-class[^\n]*" + re.escape(service_descriptor), preview),
            "Direct preview does not reference the service class declared in the manifest")
    require_in_order(preview, "Landroid/content/ComponentName;",
                     "android.service.wallpaper.CHANGE_LIVE_WALLPAPER",
                     "android.service.wallpaper.extra.LIVE_WALLPAPER_COMPONENT", "putExtra",
                     "launchWallpaperActivity", "android.service.wallpaper.LIVE_WALLPAPER_CHOOSER",
                     "launchWallpaperActivity")
    launch = method_block(activity, "launchWallpaperActivity")
    for value in ("startActivity", "Landroid/content/ActivityNotFoundException;",
                  "Ljava/lang/SecurityException;", "Landroid/util/Log;"):
        require(value in launch, f"Missing wallpaper launch or diagnostics wiring: {value}")
    print("Verified: no requested permissions, protected service and engine, compiled metadata, and preview/chooser wiring.")


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
