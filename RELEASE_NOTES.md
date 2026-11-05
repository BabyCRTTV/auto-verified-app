Auto Verified 1.0.2 temporarily pauses automatic inventory refresh attempts while dealership feed access is being arranged.

- Android no longer automatically requests dealership inventory on app launch.
- The existing **Sync new inventory** button remains available for manual checks.
- Saved and bundled vehicle listings remain available even when syncing is unavailable.
- Out-of-date inventory is identified rather than passed off as newly checked.
- The GitHub Actions inventory workflow has no hourly schedule and no push trigger, but can be run manually.
- Vehicle search, saved listings, comparison, galleries and contact functions remain.

Download **Auto-Verified-1.0.2.apk** below. This remains a development-signed APK, and upgrades require the original development signing key to have been preserved.

To restore automatic refresh, Auto Verified or DealerCenter must provide authorized inventory access or a complete approved feed. Configure the private GitHub Actions secret AUTO_VERIFIED_FEED_URL and re-enable the schedule deliberately.

Confirm vehicle availability and pricing with the dealership.
