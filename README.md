# ai-tools

AI chat assistant Android app (Bangla + English), powered by the Mistral API.

## Features
- AI chat with message bubbles and saved chat history
- Bangla + English support (replies in the language you write)
- Mistral API key configured in-app via Settings

## Get an API key
1. Sign up at [console.mistral.ai](https://console.mistral.ai)
2. Create an API key
3. In the app, tap the ⚙️ Settings icon and paste the key

## Build the APK
The APK is built automatically by GitHub Actions on every push:
1. Open the **Actions** tab in this repository
2. Select the latest **Build APK** run
3. Download the **ai-tools-debug-apk** artifact
4. Install the APK on your phone (enable "Install unknown apps" if asked)

To build locally: open the project in Android Studio and run **Build > Build APK(s)**.

## Ads (AdMob)
The app shows a banner ad using Google's **test ad IDs**, so no real revenue yet.
To earn from ads:
1. Create an account at [apps.admob.com](https://apps.admob.com) and register the app
2. In `app/src/main/res/values/strings.xml`, replace:
   - `admob_app_id` with your AdMob App ID
   - `admob_banner_unit_id` with your Banner Ad Unit ID
3. Wait for AdMob's app review — real ads then start serving
