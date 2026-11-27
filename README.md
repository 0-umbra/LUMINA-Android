# LUMINA — Android Live Wallpaper

LUMINA Cosmic is a static live wallpaper drawn with Android Canvas through the
native `WallpaperService` API. Android owns the preview and confirmation screen;
LUMINA does not draw an overlay or simulate wallpaper behavior in its launcher.

**Current phase: 1B.1 — Moto E13 compatibility investigation.** LUMINA Cosmic
remains a static wallpaper. The product direction is video-first, with audio muted
by default when video support is added; no video playback is implemented here.

## Build and download the debug APK

1. Push a feature branch or open a pull request targeting `develop`.
2. In **Actions**, open the successful **Build Debug APK** run for the change.
3. Sign in to GitHub, download the **`lumina-debug-apk`** artifact ZIP, and
   extract `app-debug.apk`. Artifacts are retained for 30 days.

CI uses JDK 17, Gradle 8.9, AGP 8.7.3, Kotlin 2.0.21 and Android SDK/Build Tools
35/35.0.0. It validates the wrapper and Gradle configuration, builds the APK,
then checks the packaged manifest, wallpaper XML, service and engine, preview/chooser wiring,
and absence of requested permissions before uploading. No secrets or paid
services are required.

Optional local build with JDK 17 and the same Android SDK packages:

```bash
./gradlew assembleDebug
python3 scripts/verify_wallpaper_apk.py app/build/outputs/apk/debug/app-debug.apk "$ANDROID_HOME/build-tools/35.0.0"
```

## Install and verify on the Moto E13 (Android 13)

1. Open the extracted APK and tap **Install**. If Android prompts you to allow
   installation from your file manager, you can revoke that allowance afterward.
   If updating from a differently signed debug APK, uninstall the old build first.
2. Open **LUMINA** and tap **Preview Live Wallpaper**. Note what appears:
   - **Android's preview:** continue to Step 3.
   - **Android's live wallpaper chooser:** select **LUMINA Cosmic**, then continue.
     If it isn't listed, report that the chooser opened but the entry was missing.
   - **A message in LUMINA:** share the exact direct preview and chooser outcomes
     and the reported feature status. Also check whether **LUMINA Cosmic** is
     available in the device's wallpaper settings.
3. Use **Set wallpaper** or **Apply** in the system UI. Verify the cosmic sky is
   visible behind the launcher icons and returns after locking and unlocking.

If ADB is already connected, capture only LUMINA's relevant logs after tapping:

```bash
adb logcat -d -s LuminaWallpaper:I CosmicWallpaper:W
```

LUMINA logs the target component, Android’s reported live wallpaper feature, and
any exception from either launch. A feature flag or a successful launch request
alone does not prove that the picker lists or can apply the wallpaper. CI checks
APK integration, not physical-device behavior.

## Android implementation

- App ID `com.lumina.wallpaper`; min SDK 23, compile/target SDK 35.
- `MainActivity` tries Android’s official component-specific preview intent, then
  the official live wallpaper chooser if the first launch fails.
- `CosmicWallpaperService` draws on the system-owned surface in lifecycle
  callbacks. It drops its renderer when the surface is destroyed, responds to
  system redraw requests and has no render loop or worker thread.
- `CosmicRenderer` uses two simple gradients and a small deterministic star field
  without bitmap assets, network access, or new libraries.
- The exported service is protected by `android.permission.BIND_WALLPAPER`.
  The app does not request this permission or any other app permission.

Development changes go through feature branches and PRs targeting `develop`.
Do not push directly to `develop` or `main` or merge without owner approval.
