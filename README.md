# LUMINA — Android Live Wallpaper

LUMINA is a native Android project in Kotlin. A later phase will add live
wallpapers through Android's official `WallpaperService` API.

**Current phase: 1A — Android Project Foundation only.**

This phase establishes a genuine, buildable Android project. It does **not**
yet implement the animated wallpaper, video playback, wallpaper preview, or
gallery. Those are future phases.

---

## What Phase 1A includes

- Native Android project in Kotlin
- Gradle with the official Android Gradle Plugin (AGP)
- Stable Gradle / JDK combination
- Correct Android manifest and package structure
- GitHub Actions workflow that builds a debug APK automatically
- No paid APIs, no paid dependencies, no secrets, no internet permission

## Project configuration

| Setting | Value |
|---|---|
| Application ID | `com.lumina.wallpaper` |
| Application name | LUMINA |
| Language | Kotlin |
| Min SDK | 23 (Android 6.0) |
| Target SDK | 35 |
| Compile SDK | 35 |
| Gradle | 8.9 |
| Android Gradle Plugin | 8.7.3 |
| Kotlin | 2.0.21 |
| JDK | 17 (Temurin) |
| App libraries | Kotlin standard library; UI uses the Android framework |
| Android Build Tools | 35.0.0 |

The minimum SDK of 23 keeps the app installable on Android 6.0 and later,
including the Moto E13 running Android 13 (API 33).

## Package structure

```text
app/src/main/java/com/lumina/wallpaper/
└── MainActivity.kt          # Foundation launcher activity (not a wallpaper)

app/src/main/
├── AndroidManifest.xml      # No permissions, no wallpaper service yet
└── res/
    ├── layout/activity_main.xml
    └── values/strings.xml, themes.xml
```

Future components are **not** implemented in Phase 1A:

- `WallpaperService` implementation
- Canvas-based animation renderer
- Native wallpaper preview
- Built-in wallpaper gallery
- Local video wallpaper playback

## How to build the APK (GitHub Actions — recommended)

LUMINA is developed entirely from an Android phone (GitHub + Termux + AI
agents). There is no PC or laptop, so APK builds happen in GitHub Actions.
No secrets, API keys, Firebase, Cloudflare, or paid services are required.

1. Push to a feature branch (for example `feature/**`) or open a pull
   request targeting `develop`.
2. Open the **Actions** tab in GitHub and watch the
   **Build Debug APK** workflow run.
3. When it finishes, open the completed run and download the
   **`lumina-debug-apk`** artifact.
4. The artifact contains `app-debug.apk`.

The workflow:

- Runs on pushes to feature branches and pull requests targeting `develop`
- Sets up JDK 17 (Temurin) and the Android SDK
- Validates the Gradle wrapper and Gradle configuration (`./gradlew help`)
- Builds the debug APK (`./gradlew assembleDebug`) and checks that it requests no permissions
- Uploads the APK as a downloadable artifact

## How to install the APK on the Moto E13

1. Sign in to GitHub, download the `lumina-debug-apk` artifact ZIP, and
   extract `app-debug.apk` using the phone's file manager.
2. On the phone, allow installation from the browser / file manager if
   prompted (Settings → Security → Install unknown apps).
3. Open the APK and tap **Install**.
4. Open **LUMINA** from the app drawer. In Phase 1A you should see a simple
   foundation screen:

   > LUMINA
   > Phase 1A — Android Project Foundation
   >
   > This is a foundation build only.
   > The animated wallpaper will be added in a later phase.

This confirms the build installs and launches. It is **not** a wallpaper yet.

## How to build locally (optional — if you ever have a PC)

Prerequisites: JDK 17, Android SDK platform 35 and Build Tools 35.0.0.

```bash
./gradlew assembleDebug
```

The APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

## Branching

- `main` — stable releases only. Never push directly.
- `develop` — integration branch. Feature PRs target `develop`.
- `feature/*` and `arena/*` — feature branches branched from `develop`.

Never merge pull requests without owner approval. Phase 1A stops for owner
approval before Phase 1B begins.

## Permissions and privacy

Phase 1A declares **no permissions** in the manifest:

- No `INTERNET`
- No dangerous permissions
- No root, no bootloader changes, no overlays, no floating windows

The app is offline-first and lightweight.

## Known limitations (Phase 1A)

- No `WallpaperService` yet — LUMINA does not appear in the system wallpaper
  picker in this phase.
- No animation, video, preview, or gallery.
- Uses the system launcher icon (`@android:drawable/sym_def_app_icon`).
  A custom LUMINA icon will be added in a later phase.
- Physical-device testing is done by the owner on the Moto E13 after
  downloading the CI-built APK. CI does not run on a physical device.

## Roadmap (future phases — not in 1A)

- **Phase 1B:** First genuine animated wallpaper via `WallpaperService`
  + Canvas renderer, verified on the Moto E13 (Android 13).
- Later: native wallpaper preview, built-in gallery, local video playback.
