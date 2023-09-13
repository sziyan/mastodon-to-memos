# Mastodon to Memos

This script will automatically grab the latest status from a mastodon profile and cross post it to a Memos instance.

# Configurations
Few environment variables are required:
- INSTANCE -> Your Mastodon instance URL
- ACCESS -> Your Mastodon application access token
- MEMOS_URL -> Your Memos server URL
- API -> Memos OpenId

This script also has optional Grist integration. As long as Grist API is enabled, all other Grist variables must be declared as well:

- GRIST_API
- GRIST_URL
- GRIST_WORKSPACE
- GRIST_DOC
- GRIST_TABLE