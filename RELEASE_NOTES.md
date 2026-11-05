Auto Verified 1.0.1 improves refresh reliability and identifies delayed inventory updates.

- Android reads the dealership inventory directly, then falls back to the published inventory feed if the website rejects direct access.
- Cached inventory is preserved if a newer feed is unavailable; older feeds cannot replace newer cached data.
- The app visibly marks outdated inventory instead of claiming old listings are current.
- The Android native bridge still accepts only verified dealership inventory URLs and a single GitHub Pages JSON resource.
- Search, filters, saved vehicles, comparison, galleries and contact links remain intact.

Download **Auto-Verified-1.0.1.apk** below. This remains a development-signed APK for direct installation. It should update 1.0.0 only if the cached development signing key was preserved.

NOTE: The website still returns HTTP 403 to GitHub-hosted automation. Automatic feed updates need a dealer-authorized DealerCenter CSV or JSON source configured through the AUTO_VERIFIED_FEED_URL Actions secret, or restored authorized access. This release does not claim to have refreshed the blocked feed.

Always confirm final vehicle prices and availability with the dealership.
