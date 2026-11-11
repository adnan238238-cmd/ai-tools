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
