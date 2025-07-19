# TikTok Integration Setup Guide

## Overview
This integration service now supports both TikTok Shop and TikTok Account integration. The TikTok Account integration allows creators to connect their TikTok accounts to sync content and analytics.

## Environment Variables

Add the following environment variables to your `.env` file:

```env
# TikTok Account Integration
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_REDIRECT_URI=http://localhost:3000/creator-dashboard/settings

# TikTok Shop Integration (existing)
TIKTOK_APP_KEY=your_tiktok_shop_app_key
TIKTOK_APP_SECRET=your_tiktok_shop_app_secret
```

## TikTok Account Integration Endpoints

### 1. Get Connection Status
```
GET /api/v1/integrations/tiktok/status/{user_id}
```

### 2. Initialize OAuth
```
POST /api/v1/integrations/tiktok/auth/init?user_id={user_id}&redirect_uri={redirect_uri}
```

### 3. Handle OAuth Callback
```
POST /api/v1/integrations/tiktok/auth/callback?code={code}&state={state}&user_id={user_id}
```

### 4. Disconnect Account
```
DELETE /api/v1/integrations/tiktok/disconnect/{user_id}
```

### 5. Sync Account Data
```
POST /api/v1/integrations/tiktok/sync/{user_id}
```

### 6. Get Account Metrics
```
GET /api/v1/integrations/tiktok/metrics/{user_id}
```

## Database Schema

The integration uses the following new table:

### TikTokAccount
- `id`: Primary key
- `user_id`: Link to our user system
- `tiktok_user_id`: TikTok user ID
- `username`: TikTok username
- `display_name`: TikTok display name
- `avatar_url`: Profile picture URL
- `follower_count`: Number of followers
- `following_count`: Number of following
- `like_count`: Total likes received
- `video_count`: Number of videos
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `access_token_expire_in`: Token expiry time
- `refresh_token_expire_in`: Refresh token expiry time
- `is_active`: Connection status
- `last_sync_at`: Last sync timestamp
- `connected_at`: Connection timestamp
- `updated_at`: Last update timestamp

## Frontend Integration

The frontend uses the `useTikTokIntegration` hook which provides:

- `isConnected`: Boolean connection status
- `connectionStatus`: Detailed connection information
- `metrics`: Account metrics
- `loading`: Loading state
- `error`: Error messages
- `connectTikTok()`: Initiate connection
- `disconnectTikTok()`: Disconnect account
- `refreshConnection()`: Sync data
- `checkConnectionStatus()`: Check status

## Setup Steps

1. **Create TikTok App**: Create a TikTok app in the TikTok Developer Console
2. **Configure OAuth**: Set up OAuth redirect URIs
3. **Environment Variables**: Add the required environment variables
4. **Database Migration**: Run database migrations to create the new table
5. **Test Integration**: Test the connection flow

## Testing

You can test the integration by:

1. Starting the integration service
2. Navigating to the creator dashboard settings
3. Clicking "Connect TikTok" in the integrations tab
4. Following the OAuth flow
5. Verifying the connection status and metrics

## Error Handling

The integration includes comprehensive error handling for:
- OAuth failures
- Token refresh issues
- API rate limits
- Network errors
- Database errors

## Security Notes

- Tokens are stored securely in the database
- Automatic token refresh is implemented
- OAuth state validation is enforced
- All endpoints include proper error handling 