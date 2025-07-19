// hooks/useTikTokIntegration.ts - TikTok integration hook

import { useState, useEffect } from 'react'
import { integrationServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'
import { useAuth } from './useAuth'

interface TikTokConnectionStatus {
  status: 'active' | 'error' | 'pending' | 'disconnected'
  username?: string
  userId?: string
  connectedAt?: string
  lastSync?: string
  error?: string
}

interface TikTokMetrics {
  followers: number
  following: number
  likes: number
  videos: number
  lastUpdated: string
}

interface TikTokAuthResponse {
  authUrl: string
  state: string
}

export function useTikTokIntegration() {
  const { user } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<TikTokConnectionStatus | null>(null)
  const [metrics, setMetrics] = useState<TikTokMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check connection status on component mount
  useEffect(() => {
    if (user?.id) {
      checkConnectionStatus()
    }
  }, [user?.id])

  const checkConnectionStatus = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<TikTokConnectionStatus> = await integrationServiceClient.get(
        `/api/v1/integrations/tiktok/status/${user?.id}`
      )

      if (response.success && response.data) {
        setConnectionStatus(response.data)
        setIsConnected(response.data.status === 'active')
      } else {
        setIsConnected(false)
        setConnectionStatus({ status: 'disconnected' })
      }
    } catch (err: any) {
      console.error('Failed to check TikTok connection status:', err)
      setError('Failed to check connection status')
      setIsConnected(false)
    } finally {
      setLoading(false)
    }
  }

  const connectTikTok = async () => {
    try {
      setLoading(true)
      setError(null)

      // Step 1: Get TikTok auth URL
      const authResponse: ApiResponse<TikTokAuthResponse> = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/auth/init?user_id=${user?.id}&redirect_uri=${encodeURIComponent(`${window.location.origin}/creator-dashboard/settings?tab=integrations`)}`
      )

      if (authResponse.success && authResponse.data) {
        // Step 2: Redirect to TikTok OAuth
        window.location.href = authResponse.data.authUrl
      } else {
        throw new Error(authResponse.error || 'Failed to initialize TikTok authentication')
      }
    } catch (err: any) {
      console.error('Failed to connect TikTok:', err)
      setError(err.message || 'Failed to connect TikTok')
    } finally {
      setLoading(false)
    }
  }

  const disconnectTikTok = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<any> = await integrationServiceClient.delete(
        `/api/v1/integrations/tiktok/disconnect/${user?.id}`
      )

      if (response.success) {
        setIsConnected(false)
        setConnectionStatus({ status: 'disconnected' })
        setMetrics(null)
      } else {
        throw new Error(response.error || 'Failed to disconnect TikTok')
      }
    } catch (err: any) {
      console.error('Failed to disconnect TikTok:', err)
      setError(err.message || 'Failed to disconnect TikTok')
    } finally {
      setLoading(false)
    }
  }

  const refreshConnection = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<any> = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/sync/${user?.id}`
      )

      if (response.success) {
        // Refresh connection status and metrics
        await checkConnectionStatus()
        await fetchMetrics()
      } else {
        throw new Error(response.error || 'Failed to sync TikTok data')
      }
    } catch (err: any) {
      console.error('Failed to refresh TikTok connection:', err)
      setError(err.message || 'Failed to sync TikTok data')
    } finally {
      setLoading(false)
    }
  }

  const fetchMetrics = async () => {
    if (!isConnected) return

    try {
      const response: ApiResponse<TikTokMetrics> = await integrationServiceClient.get(
        `/api/v1/integrations/tiktok/metrics/${user?.id}`
      )

      if (response.success && response.data) {
        setMetrics(response.data)
      }
    } catch (err: any) {
      console.error('Failed to fetch TikTok metrics:', err)
    }
  }

  // Handle OAuth callback
  const handleOAuthCallback = async (code: string, state: string) => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<TikTokConnectionStatus> = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/auth/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}&user_id=${user?.id}`
      )

      if (response.success && response.data) {
        setConnectionStatus(response.data)
        setIsConnected(response.data.status === 'active')
        await fetchMetrics()
      } else {
        throw new Error(response.error || 'Failed to complete TikTok authentication')
      }
    } catch (err: any) {
      console.error('Failed to handle OAuth callback:', err)
      setError(err.message || 'Failed to complete TikTok authentication')
    } finally {
      setLoading(false)
    }
  }

  // Check for OAuth callback parameters on page load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    
    if (code && state && user?.id) {
      handleOAuthCallback(code, state)
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [user?.id])

  return {
    isConnected,
    connectionStatus,
    metrics,
    loading,
    error,
    connectTikTok,
    disconnectTikTok,
    refreshConnection,
    checkConnectionStatus,
    fetchMetrics,
  }
} 