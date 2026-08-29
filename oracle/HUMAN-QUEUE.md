# Human Queue — Accounts to Open

## For Oracle Data Ingestion (can do now)

| # | Platform | Action | URL | What It Unlocks |
|---|----------|--------|-----|-----------------|
| 1 | **Roblox** | Create account → Open Cloud → API key | create.roblox.com | Creator Store search + asset management |
| 2 | **Gumroad** | Create seller → Settings → API → key | gumroad.com | Product catalog, sales data |
| 3 | **itch.io** | Create account → My API Keys → key | itch.io | Games/assets catalog, butler CLI |
| 4 | **Discord** | Create developer app → enable monetization | discord.com/developers | App catalog, bot analytics |
| 5 | **YouTube** | Google Cloud → YouTube Data API → OAuth | console.cloud.google.com | Video analytics, trends |
| 6 | **TikTok** | Developer account → Content Posting API | developers.tiktok.com | Video publishing |
| 7 | **Apple** | Apple Developer → App Store Connect API key | developer.apple.com | App Store catalog |
| 8 | **Google Play** | Google Cloud → Android Publisher API → OAuth | console.cloud.google.com | Play Store catalog |
| 9 | **AWS** | AWS seller account → Catalog API | aws.amazon.com/marketplace | Enterprise SaaS catalog |
| 10 | **Wix** | Developer account → App Market API | dev.wix.com | Web app catalog |
| 11 | **monday.com** | Developer account → GraphQL API | developer.monday.com | Workflow app catalog |
| 12 | **Microsoft** | Partner Center → SaaS Fulfillment API | partner.microsoft.com | Teams app catalog |
| 13 | **Patreon** | Creator account → API v2 (NOT v1, retiring Oct 2026) | patreon.com | Memberships data |
| 14 | **Adobe** | Adobe I/O → OAuth 2.0 | console.adobe.io | Stock content catalog |
| 15 | **Fab** | Epic Games account | epicgames.com | Asset marketplace (manual) |
| 16 | **Unity** | Publisher account | publisher.unity.com | Asset Store (manual) |
| 17 | **Canva** | Apply to Creators program | canva.com/creators | Templates (manual) |
| 18 | **Creative Market** | Seller account | creativemarket.com | Design templates (manual) |
| 19 | **Udemy** | Instructor account | udemy.com | Courses (read-only API) |
| 20 | **KDP** | KDP account | kdp.amazon.com | Books (no API) |
| 21 | **Apify** | Apify account → API key | apify.com | Web scraping actors |
| 22 | **Etsy** | Etsy seller account → API key | etsy.com | Handmade/vintage goods |
| 23 | **Webflow** | Webflow account → API token | webflow.com | Website builder |
| 24 | **Superhive** | Blender marketplace account | superhive.com | Blender assets |
| 25 | **Bittensor** | No account needed — SDK reads chain data directly | pip install bittensor | Subnet economics |

## Environment Variables

```bash
# Priority 1 — set these first
ROBLOX_API_KEY=
GUMROAD_API_KEY=
ITCH_API_KEY=
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # set via env var
DISCORD_TOKEN=
DISCORD_CLIENT_ID=

# Priority 2
YOUTUBE_API_KEY=
TIKTOK_ACCESS_TOKEN=
APPLE_CONNECT_API_KEY=
GOOGLE_PLAY_SERVICE_ACCOUNT=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=

# Priority 3
WIX_API_KEY=
MONDAY_API_TOKEN=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=
PATREON_ACCESS_TOKEN=
ADOBE_CLIENT_ID=
ADOBE_CLIENT_SECRET=
```

## Status

| Platform | Account | API Key | Ingestion |
|----------|---------|---------|-----------|
| GitHub | ✅ | ✅ ghp_... | ✅ 100 items |
| BountyBook | ✅ | ✅ free API | ✅ 131 items |
| the402 | ✅ | ✅ free API | ✅ 100 items |
| x402engine | ✅ | ✅ free API | ✅ 110 items |
| Agent402 | ✅ | ✅ free API | ✅ 2 items |
| PayAPI | ✅ | ✅ free API | ✅ 75 items |
| Roblox | ❌ | ❌ | ❌ |
| Gumroad | ❌ | ❌ | ❌ |
| itch.io | ❌ | ❌ | ❌ |
| Discord | ❌ | ❌ | ❌ |
| YouTube | ❌ | ❌ | ❌ |
| Bittensor | ✅ | ✅ SDK | ❌ (needs testing) |
