# LUMINA — Android Live Wallpaper

LUMINA Cosmic is a static live wallpaper drawn with Android Canvas through the
native `WallpaperService` API. Android owns the preview and confirmation screen;
LUMINA does not draw an overlay or simulate wallpaper behavior in its launcher.

**Current phase: 1B — one native static live wallpaper.** No animation, gallery,
customization, or video playback yet.

## Build and download the debug APK

1. Push a feature branch or open a pull request targeting `develop`.
2. In **Actions**, open the successful **Build Debug APK** run for the change.
3. Sign in to GitHub, download the **`lumina-debug-apk`** artifact ZIP, and
   extract `app-debug.apk`. Artifacts are retained for 30 days.

CI uses JDK 17, Gradle 8.9, AGP 8.7.3, Kotlin 2.0.21 and Android SDK/Build Tools
35/35.0.0. It validates the wrapper and Gradle configuration, builds the APK,
then checks the packaged manifest, wallpaper XML, service class, preview wiring,
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
2. Open **LUMINA** and tap **Preview Live Wallpaper**. Android's own wallpaper
   preview should show a dark sky with soft blue and violet glows and faint stars.
3. Use the system's **Set wallpaper** or **Apply** confirmation and choose a
   destination if prompted. Return to the home screen and verify that the
   wallpaper is visible behind the launcher icons.
4. Open another app, lock/unlock the phone and return home. Check that the
   wallpaper returns without a blank frame. If the preview isn't available,
   check the system wallpaper picker for **LUMINA Cosmic**; exact menus and
   live-wallpaper support depend on the device's system software.

CI checks the APK, not device behavior. The owner verifies preview and installation
on the physical Moto E13.

## Android implementation

- App ID `com.lumina.wallpaper`; min SDK 23, compile/target SDK 35.
- `MainActivity` launches the official preview intent with the service component.
- `CosmicWallpaperService` draws on the system-owned surface in lifecycle
  callbacks. It drops its renderer when the surface is destroyed, responds to
  system redraw requests and has no render loop or worker thread.
- `CosmicRenderer` uses two simple gradients and a small deterministic star field
  without bitmap assets, network access, or new libraries.
- The exported service is protected by `android.permission.BIND_WALLPAPER`.
  The app does not request this permission or any other app permission.

Development changes go through feature branches and PRs targeting `develop`.
Do not push directly to `develop` or `main` or merge without owner approval.
