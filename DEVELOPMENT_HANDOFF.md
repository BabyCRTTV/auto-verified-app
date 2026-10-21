# Auto Verified 1.0.0 handoff

Repository: BabyCRTTV/auto-verified-app. Browser: https://babycrttv.github.io/auto-verified-app/

Shared source lives in web/. Native Android shell: android/. No npm dependencies. Published signed development APK v1.0.0. Production signing is not configured; retain the cached debug signing identity or configure a backed-up release key before wider release.

Android sync fetches the public inventory and detail pages directly through a host-restricted Java bridge; UI imports with DOMParser. Browser sync reloads the JSON feed; GitHub Actions refreshes that feed hourly. Display source timestamp and preserve the last successful feed on import failure. Never call a browser feed reload a direct dealership sync.

Use dealership total prices including processing fees. Disclose excluded taxes, title, registration. Do not fabricate stock, specs, photos, prices, hours, or availability. Outside phone/text links must only open the user's apps. Financing stays on the dealer website.

Validation completed: five Python inventory tests, JS syntax check, browser search/filter/save/detail/photo/compare flows, phone layout inspection, native import path with captured dealer HTML, successful Android build and Pages deployment. APK ZIP contents and SHA256 match published artifact. Actual Android runtime/networking has not been tested on a device or emulator.

CI uses ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager (not a bare sdkmanager command or obsolete tools package), Java 17, Gradle 8.9, AGP 8.7.3.
