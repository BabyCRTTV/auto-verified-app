# Auto Verified 1.0.2 handoff

Repository: BabyCRTTV/auto-verified-app. Browser: https://babycrttv.github.io/auto-verified-app/

Shared source lives in web/. Native Android shell: android/. No npm dependencies. Published signed development APK v1.0.0. Production signing is not configured; retain the cached debug signing identity or configure a backed-up release key before wider release.

Android sync fetches the public inventory and detail pages directly through a host-restricted Java bridge; UI imports with DOMParser. Browser sync reloads the published JSON feed; the GitHub Actions inventory refresh is paused (manual dispatch only). Display source timestamp and preserve the last successful feed on import failure. Never call a browser feed reload a direct dealership sync.

Use dealership total prices including processing fees. Disclose excluded taxes, title, registration. Do not fabricate stock, specs, photos, prices, hours, or availability. Outside phone/text links must only open the user's apps. Financing stays on the dealer website.

Validation completed: five Python inventory tests, JS syntax check, browser search/filter/save/detail/photo/compare flows, phone layout inspection, native import path with captured dealer HTML, successful Android build and Pages deployment. APK ZIP contents and SHA256 match published artifact. Actual Android runtime/networking has not been tested on a device or emulator.

CI uses ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager (not a bare sdkmanager command or obsolete tools package), Java 17, Gradle 8.9, AGP 8.7.3.

## 1.0.1 refresh recovery

The dealership returns HTTP 403 to GitHub Actions even with normal HTML request headers. Repository secret AUTO_VERIFIED_FEED_URL now supports a dealer-authorized full HTTPS CSV/JSON inventory export. Until an authorized feed is provided, the inventory job has no automatic triggers; an explicitly started manual run will still fail under HTTP 403. Automatic publishing of stale dealership data is not attempted. tests/test_inventory.py covers both imports and fail-safe behavior. See README for feed schema.

Android falls back to https://babycrttv.github.io/auto-verified-app/inventory.json through its allowlisted native bridge if direct dealership access fails. The UI indicates inventory older than 48 hours and never replaces a newer cached copy with older data. Confirm native runtime and APK signing continuity on a physical phone. Release v1.0.1 uses versionCode 2.

## 1.0.2 pause, November 5, 2026

Per user request, remove both schedule and push triggers from `.github/workflows/inventory.yml`, leaving only `workflow_dispatch`. Do not silently re-enable until the dealer-authorized CSV/JSON feed exists and is tested. In `web/app.js`, remove the `sync(true)` call during initialization for both native Android and browser; initial inventory loading from local packaged JSON/cache remains intact. Manual button continues to call `sync()`. Build versionCode 3/versionName 1.0.2 and release with existing development signing identity. IMPORTANT: installed older APKs can continue to request refresh on open until they are updated to 1.0.2.
