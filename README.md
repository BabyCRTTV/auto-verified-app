# Auto Verified

A responsive vehicle-shopping companion for [Auto Verified LLC](https://www.carsforyouva.com/) in Richmond, Virginia. Built by 8BitTrade.

- [Open the browser app](https://babycrttv.github.io/auto-verified-app/)
- [Download the Android APK](https://github.com/BabyCRTTV/auto-verified-app/releases/latest)

## Features

Search real inventory, filter by body style/make/budget/mileage, sort results, save a shortlist locally, compare up to three vehicles, and browse photo galleries. Call, text, and directions open the relevant external app; no enquiry is sent automatically. Credit applications stay on the dealership website.

## Inventory sync

Android's **Sync new inventory** button reads the public dealership inventory and vehicle pages directly over HTTPS. It replaces inventory only after the complete import succeeds. New, changed, and removed listings are reflected. A cached feed is bundled for first launch; the last good inventory is retained offline. Saved IDs are kept locally, and vehicles no longer in inventory disappear from active saved results.

Android 1.0.2 does not automatically contact the dealership when the app opens. It displays locally saved inventory or the packaged feed until the user presses **Sync new inventory**. Manual Android sync tries the dealership and falls back to the published GitHub Pages feed if access is blocked; an older feed cannot replace newer saved data. Inventory more than 48 hours old is marked delayed. The browser app loads its published `inventory.json` to display listings; its **Sync new inventory** button reloads that published file only. **The GitHub Actions inventory refresh schedule and push triggers are paused until the dealership provides an authorized feed.** The inventory workflow can only be started manually from Actions. Browser sync does not start that workflow or bypass cross-origin restrictions. The displayed timestamp indicates source freshness, not the time the button was tapped.

The parser fails on an empty feed, duplicate stock IDs, or a mismatched advertised listing count. Pagination or a dealer redesign may require a parser update. Prices use the dealer's `data-total-price` field, including the displayed dealer processing fees. Additional taxes/title/registration are disclosed. No valuations or availability claims are invented.

## Development

The shared UI is plain HTML, CSS and JavaScript under `web/`, with no build dependencies. Run `python -m http.server 8080 --directory web` and open localhost:8080. Run `node --check web/app.js` and `python -m unittest discover -s tests` for checks. Update inventory with `python scripts/sync_inventory.py` (Python 3.10+, standard library only).

Android uses a small native Java WebView shell, compile/target SDK 35, minimum API 26, AGP 8.7.3 and Gradle 8.9. From `android/`, run `gradle assembleDebug`. GitHub Actions builds and publishes the APK and browser app on source changes. The shared UI is packaged in the APK, rather than opening a hosted webpage.

Only INTERNET permission is requested. The native bridge accepts HTTPS inventory paths on the fixed dealership host, refuses redirects, limits response sizes, and is exposed only to the bundled local UI. Outside navigation opens the browser or phone app. There is no remote analytics code, account system, tracking SDK, or personal-data collection. Vehicle photos are served by the dealer image provider; optional typography loads from Google Fonts.

## Signing and distribution

Releases 1.0.0 and 1.0.1 use a **development APK**, suitable for direct testing, not a production Play Store submission. Actions caches the development signing key for subsequent builds; caches can expire, so production updates must migrate to a securely backed-up release signing key in GitHub Actions secrets before wider distribution. If the development key is lost, Android requires uninstalling the old development build before installing a differently signed build. Export saved items before uninstalling if needed (there is no export UI in 1.0).

Vehicle data, photos and dealership branding remain the property of their respective owners. This project does not modify the dealership website or imply dealership endorsement.

## Dealer-authorized feed (recommended)

GitHub-hosted inventory refresh requests currently receive HTTP 403 from the dealership even with normal HTML request headers. The durable solution is a dealer-approved complete HTTPS CSV or JSON inventory export. Ask the Auto Verified DealerCenter administrator or DealerCenter support for an export intended for this app. Do not put private feed URLs or tokens into repository files.

Add the authorized HTTPS URL as a GitHub Actions repository secret named AUTO_VERIFIED_FEED_URL. The hourly inventory workflow will then import from that source instead of the blocked dealership HTML page. Without the secret, the original site reader remains active.

The importer accepts a CSV with column headers or JSON arrays / an object containing a vehicles array. Every car needs a unique stock ID, year, make, model, full https://www.carsforyouva.com/inventory/ listing URL, and HTTPS image. Optional columns include mileage, VIN, trim, engine, transmission, drivetrain, color, body style and pipe-separated photo_urls. Price fields must be fee-inclusive: provide total_price, price_including_fees, or both internet_price and dealer_fee. If the export has only a base price, the app will display Call for price rather than misrepresent it as fee-inclusive.

Supply the entire active inventory with each export. Empty, duplicate, malformed, or invalid records fail before replacing the saved feed. The Android direct website importer remains a separate path.

### Temporarily paused automatic inventory refresh

Paused on November 5, 2026 because the dealer website rejects GitHub-hosted inventory requests (HTTP 403). `.github/workflows/inventory.yml` has **only `workflow_dispatch`**, with no `schedule` or `push` trigger. This is independent of the normal app-build workflow, which still builds source changes. To resume after receiving an authorized feed, save the URL securely as the `AUTO_VERIFIED_FEED_URL` repository Actions secret, then explicitly restore an appropriate schedule in inventory.yml. Android 1.0.2 no longer tries direct dealer sync automatically on app launch; users can still tap **Sync new inventory** manually. Previously installed APK versions do not change until updated.
