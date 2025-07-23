// hooks/useTikTokIntegration.ts - Development version with debugging
import { useState, useEffect, useCallback, useRef } from 'react'
import { integrationServiceClient } from '@/lib/api/client'
import { useAuth } from '@/context/authContext'

// Development mode flag
const DEV_MODE = process.env.NODE_ENV === 'development'

// Dev logger utility
const devLog = (message: string, data?: any) => {
  if (DEV_MODE) {
    console.log(`🔧 [TikTok Integration] ${message}`, data || '')
  }
}

// Type definitions
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

// API Response types - matching your backend structure
interface BaseApiResponse<T> {
  success: boolean
  data?: T
  error?: string | null
  statusCode?: number
}

// Your backend returns nested structure
interface NestedApiResponse<T> {
  success: boolean
  data?: {
    success: boolean
    data?: T
  }
  error?: string | null
  statusCode?: number
}

// Specific response types
type TikTokAuthResponse = NestedApiResponse<{
  authUrl: string
  state: string
}>

type TikTokStatusResponse = BaseApiResponse<TikTokConnectionStatus>

type TikTokMetricsResponse = BaseApiResponse<TikTokMetrics>

// Error types for better debugging
enum TikTokErrorType {
  AUTH_INIT_FAILED = 'AUTH_INIT_FAILED',
  INVALID_STATE = 'INVALID_STATE',
  MISSING_CODE_VERIFIER = 'MISSING_CODE_VERIFIER',
  CALLBACK_FAILED = 'CALLBACK_FAILED',
  CONNECTION_CHECK_FAILED = 'CONNECTION_CHECK_FAILED',
  METRICS_FETCH_FAILED = 'METRICS_FETCH_FAILED',
  DISCONNECT_FAILED = 'DISCONNECT_FAILED',
  SYNC_FAILED = 'SYNC_FAILED'
}

class TikTokError extends Error {
  constructor(
    public type: TikTokErrorType,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'TikTokError'
  }
}

// PKCE helper functions
class PKCEUtils {
  static generateRandomString(length: number): string {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    let result = ''
    const randomValues = new Uint8Array(length)
    crypto.getRandomValues(randomValues)
    
    for (let i = 0; i < length; i++) {
      result += charset.charAt(randomValues[i] % charset.length)
    }
    
    devLog('Generated random string', { length, preview: result.substring(0, 10) + '...' })
    return result
  }

  static async generateCodeChallenge(codeVerifier: string): Promise<string> {
    const encoder = new TextEncoder()
    const data = encoder.encode(codeVerifier)
    const digest = await crypto.subtle.digest('SHA-256', data)
    const challenge = btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '')
    
    devLog('Generated code challenge', { 
      verifierLength: codeVerifier.length,
      challengeLength: challenge.length 
    })
    
    return challenge
  }
}

// Storage manager for OAuth data
class OAuthStorage {
  private static readonly KEYS = {
    codeVerifier: 'tiktok_code_verifier',
    state: 'tiktok_oauth_state',
    timestamp: 'tiktok_oauth_timestamp'
  } as const

  static store(codeVerifier: string, state: string): void {
    try {
      sessionStorage.setItem(this.KEYS.codeVerifier, codeVerifier)
      sessionStorage.setItem(this.KEYS.state, state)
      sessionStorage.setItem(this.KEYS.timestamp, Date.now().toString())
      
      devLog('OAuth data stored', { 
        state: state.substring(0, 10) + '...',
        timestamp: new Date().toISOString()
      })
    } catch (error) {
      console.error('Failed to store OAuth data:', error)
    }
  }

  static retrieve(): { codeVerifier: string | null; state: string | null; timestamp: string | null } {
    const data = {
      codeVerifier: sessionStorage.getItem(this.KEYS.codeVerifier),
      state: sessionStorage.getItem(this.KEYS.state),
      timestamp: sessionStorage.getItem(this.KEYS.timestamp)
    }
    
    devLog('OAuth data retrieved', {
      hasCodeVerifier: !!data.codeVerifier,
      hasState: !!data.state,
      storedAt: data.timestamp ? new Date(parseInt(data.timestamp)).toISOString() : null
    })
    
    return data
  }

  static clear(): void {
    sessionStorage.removeItem(this.KEYS.codeVerifier)
    sessionStorage.removeItem(this.KEYS.state)
    sessionStorage.removeItem(this.KEYS.timestamp)
    
    devLog('OAuth data cleared')
  }

  static isExpired(): boolean {
    const timestamp = sessionStorage.getItem(this.KEYS.timestamp)
    if (!timestamp) return true
    
    const elapsed = Date.now() - parseInt(timestamp)
    const expired = elapsed > 10 * 60 * 1000 // 10 minutes
    
    devLog('OAuth data expiry check', {
      elapsed: `${Math.floor(elapsed / 1000)}s`,
      expired
    })
    
    return expired
  }
}

// API client with retry logic
class TikTokAPIClient {
  private static async retryableRequest<T>(
    fn: () => Promise<T>,
    retries = 3,
    delay = 1000
  ): Promise<T> {
    try {
      const result = await fn()
      devLog('API request successful', { retries: 3 - retries })
      return result
    } catch (error) {
      if (retries > 0) {
        devLog(`API request failed, retrying... (${retries} left)`, error)
        await new Promise(resolve => setTimeout(resolve, delay))
        return this.retryableRequest(fn, retries - 1, delay * 2)
      }
      throw error
    }
  }

  // Helper to extract data from nested responses
  private static extractData<T>(response: any): T | undefined {
    // Handle nested structure: response.data.data or response.data
    if (response.data?.data !== undefined) {
      return response.data.data
    }
    return response.data
  }

  static async checkStatus(userId: string): Promise<TikTokStatusResponse> {
    devLog('Checking TikTok connection status', { userId })
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.get(
        `/api/v1/integrations/tiktok/status/${userId}`
      )
      
      const processedResponse: TikTokStatusResponse = {
        success: response.success,
        data: this.extractData<TikTokConnectionStatus>(response),
        error: response.error
      }
      
      devLog('Status check response', processedResponse)
      return processedResponse
    })
  }

  static async initAuth(params: URLSearchParams): Promise<TikTokAuthResponse> {
    devLog('Initializing TikTok auth', Object.fromEntries(params))
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/auth/init?${params.toString()}`
      )
      
      devLog('Auth init response', response)
      return response as TikTokAuthResponse
    })
  }

  static async completeAuth(params: URLSearchParams): Promise<TikTokStatusResponse> {
    devLog('Completing TikTok auth', {
      hasCode: params.has('code'),
      hasState: params.has('state'),
      hasVerifier: params.has('code_verifier')
    })
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/auth/callback?${params.toString()}`
      )
      
      const processedResponse: TikTokStatusResponse = {
        success: response.success,
        data: this.extractData<TikTokConnectionStatus>(response),
        error: response.error
      }
      
      devLog('Auth complete response', processedResponse)
      return processedResponse
    })
  }

  static async disconnect(userId: string): Promise<BaseApiResponse<void>> {
    devLog('Disconnecting TikTok', { userId })
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.delete(
        `/api/v1/integrations/tiktok/disconnect/${userId}`
      )
      
      devLog('Disconnect response', response)
      return response as BaseApiResponse<void>
    })
  }

  static async sync(userId: string): Promise<BaseApiResponse<void>> {
    devLog('Syncing TikTok data', { userId })
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/sync/${userId}`
      )
      
      devLog('Sync response', response)
      return response as BaseApiResponse<void>
    })
  }

  static async fetchMetrics(userId: string): Promise<TikTokMetricsResponse> {
    devLog('Fetching TikTok metrics', { userId })
    
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.get(
        `/api/v1/integrations/tiktok/metrics/${userId}`
      )
      
      const processedResponse: TikTokMetricsResponse = {
        success: response.success,
        data: this.extractData<TikTokMetrics>(response),
        error: response.error
      }
      
      devLog('Metrics response', processedResponse)
      return processedResponse
    })
  }

  static async syncVideos(creatorId: string): Promise<BaseApiResponse<any>> {
    devLog('Syncing TikTok videos', { creatorId })
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/sync/videos/${creatorId}`
      )
      devLog('Sync videos response', response)
      return response as BaseApiResponse<any>
    })
  }

  static async markDeliverable(videoId: string, deliverableId: string, creatorId: string): Promise<BaseApiResponse<any>> {
    devLog('Marking video as deliverable', { videoId, deliverableId, creatorId })
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/mark/deliverable/${videoId}/${deliverableId}/${creatorId}`
      )
      devLog('Mark deliverable response', response)
      return response as BaseApiResponse<any>
    })
  }

  static async attributeGMV(creatorId: string): Promise<BaseApiResponse<any>> {
    devLog('Attributing GMV to creator', { creatorId })
    return this.retryableRequest(async () => {
      const response = await integrationServiceClient.post(
        `/api/v1/integrations/tiktok/attribute/gmv/${creatorId}`
      )
      devLog('Attribute GMV response', response)
      return response as BaseApiResponse<any>
    })
  }
}

export function useTikTokIntegration() {
  const { user } = useAuth()
  const abortControllerRef = useRef<AbortController | null>(null)
  
  // State management
  const [mounted, setMounted] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<TikTokConnectionStatus | null>(null)
  const [metrics, setMetrics] = useState<TikTokMetrics | null>(null)
  const [loading, setLoading] = useState<{
    checkStatus: boolean
    connect: boolean
    disconnect: boolean
    sync: boolean
    metrics: boolean
  }>({
    checkStatus: false,
    connect: false,
    disconnect: false,
    sync: false,
    metrics: false
  })
  const [error, setError] = useState<TikTokError | null>(null)

  // Dev mode state inspector
  useEffect(() => {
    if (DEV_MODE) {
      console.group('🔍 TikTok Integration State')
      console.log('Mounted:', mounted)
      console.log('Connected:', isConnected)
      console.log('Status:', connectionStatus)
      console.log('Metrics:', metrics)
      console.log('Loading:', loading)
      console.log('Error:', error)
      console.groupEnd()
    }
  }, [mounted, isConnected, connectionStatus, metrics, loading, error])

  // Set mounted state
  useEffect(() => {
    setMounted(true)
    devLog('Component mounted')
    
    return () => {
      // Cleanup abort controller
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
        devLog('Aborted pending requests on unmount')
      }
    }
  }, [])

  // Check connection status on mount
  useEffect(() => {
    if (mounted && user?.id) {
      checkConnectionStatus()
    }
  }, [mounted, user?.id])

  const checkConnectionStatus = useCallback(async () => {
    if (!user?.id) {
      devLog('Skipping status check - no user ID')
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, checkStatus: true }))
      setError(null)
      
      const response = await TikTokAPIClient.checkStatus(user.id)
      
      if (response.success && response.data) {
        setConnectionStatus(response.data)
        setIsConnected(response.data.status === 'active')
        
        if (response.data.status === 'active') {
          // Fetch metrics if connected
          fetchMetrics()
        }
      } else {
        setIsConnected(false)
        setConnectionStatus({ status: 'disconnected' })
      }
    } catch (err: any) {
      const error = new TikTokError(
        TikTokErrorType.CONNECTION_CHECK_FAILED,
        'Failed to check TikTok connection status',
        err
      )
      setError(error)
      setIsConnected(false)
      console.error(error)
    } finally {
      setLoading(prev => ({ ...prev, checkStatus: false }))
    }
  }, [user?.id])

  const connectTikTok = useCallback(async () => {
    if (!mounted || !user?.id) {
      devLog('Cannot connect - not mounted or no user ID')
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, connect: true }))
      setError(null)
      
      // Check if window exists (client-side only)
      if (typeof window === 'undefined') {
        throw new TikTokError(
          TikTokErrorType.AUTH_INIT_FAILED,
          'This action can only be performed in the browser'
        )
      }
      
      // Check for expired OAuth data
      if (!OAuthStorage.isExpired()) {
        const existing = OAuthStorage.retrieve()
        if (existing.codeVerifier && existing.state) {
          devLog('Found existing OAuth session, clearing...')
          OAuthStorage.clear()
        }
      }
      
      // Generate PKCE parameters
      const codeVerifier = PKCEUtils.generateRandomString(128)
      const codeChallenge = await PKCEUtils.generateCodeChallenge(codeVerifier)
      const oauthState = PKCEUtils.generateRandomString(32)
      
      // Store OAuth data
      OAuthStorage.store(codeVerifier, oauthState)
      
      // Build redirect URI
      const redirectUri = `${window.location.origin}/creator-dashboard/settings?tab=integrations`
      
      const authParams = new URLSearchParams({
        user_id: user.id,
        redirect_uri: redirectUri,
        code_challenge: codeChallenge,
        code_challenge_method: 'S256',
        state: oauthState
      })
      
      devLog('Initiating OAuth flow', {
        redirectUri,
        state: oauthState.substring(0, 10) + '...',
        challengeMethod: 'S256'
      })
      
      const authResponse = await TikTokAPIClient.initAuth(authParams)
      
      // Extract the nested auth data
      let authUrl: string | undefined
      let authState: string | undefined
      
      // Handle the nested response structure from your backend
      if (authResponse.data?.data) {
        authUrl = authResponse.data.data.authUrl
        authState = authResponse.data.data.state
      } else if (authResponse.data) {
        authUrl = (authResponse.data as any).authUrl
        authState = (authResponse.data as any).state
      }
      
      if (authResponse.success && authUrl) {
        devLog('Redirecting to TikTok OAuth', {
          url: authUrl.substring(0, 50) + '...',
          state: authState
        })
        
        // Redirect to TikTok OAuth
        window.location.href = authUrl
      } else {
        throw new TikTokError(
          TikTokErrorType.AUTH_INIT_FAILED,
          authResponse.error || 'Failed to initialize TikTok authentication',
          authResponse
        )
      }
    } catch (err: any) {
      const error = err instanceof TikTokError ? err : new TikTokError(
        TikTokErrorType.AUTH_INIT_FAILED,
        err.message || 'Failed to connect TikTok',
        err
      )
      setError(error)
      OAuthStorage.clear()
      console.error(error)
    } finally {
      setLoading(prev => ({ ...prev, connect: false }))
    }
  }, [mounted, user?.id])

  const disconnectTikTok = useCallback(async () => {
    if (!mounted || !user?.id) {
      devLog('Cannot disconnect - not mounted or no user ID')
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, disconnect: true }))
      setError(null)
      
      const response = await TikTokAPIClient.disconnect(user.id)
      
      if (response.success) {
        setIsConnected(false)
        setConnectionStatus({ status: 'disconnected' })
        setMetrics(null)
        OAuthStorage.clear()
        
        devLog('Successfully disconnected TikTok')
      } else {
        throw new TikTokError(
          TikTokErrorType.DISCONNECT_FAILED,
          response.error || 'Failed to disconnect TikTok',
          response
        )
      }
    } catch (err: any) {
      const error = err instanceof TikTokError ? err : new TikTokError(
        TikTokErrorType.DISCONNECT_FAILED,
        err.message || 'Failed to disconnect TikTok',
        err
      )
      setError(error)
      console.error(error)
    } finally {
      setLoading(prev => ({ ...prev, disconnect: false }))
    }
  }, [mounted, user?.id])

  const refreshConnection = useCallback(async () => {
    if (!mounted || !user?.id) {
      devLog('Cannot refresh - not mounted or no user ID')
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, sync: true }))
      setError(null)
      
      const response = await TikTokAPIClient.sync(user.id)
      
      if (response.success) {
        devLog('Successfully synced TikTok data')
        
        // Refresh connection status and metrics
        await checkConnectionStatus()
        await fetchMetrics()
      } else {
        throw new TikTokError(
          TikTokErrorType.SYNC_FAILED,
          response.error || 'Failed to sync TikTok data',
          response
        )
      }
    } catch (err: any) {
      const error = err instanceof TikTokError ? err : new TikTokError(
        TikTokErrorType.SYNC_FAILED,
        err.message || 'Failed to sync TikTok data',
        err
      )
      setError(error)
      console.error(error)
    } finally {
      setLoading(prev => ({ ...prev, sync: false }))
    }
  }, [mounted, user?.id, checkConnectionStatus])

  const fetchMetrics = useCallback(async () => {
    if (!mounted || !isConnected || !user?.id) {
      devLog('Cannot fetch metrics - not ready', {
        mounted,
        isConnected,
        hasUserId: !!user?.id
      })
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, metrics: true }))
      
      const response = await TikTokAPIClient.fetchMetrics(user.id)
      
      if (response.success && response.data) {
        setMetrics(response.data)
        devLog('Metrics updated', response.data)
      }
    } catch (err: any) {
      // Don't set error state for metrics fetch failure
      devLog('Failed to fetch metrics', err)
    } finally {
      setLoading(prev => ({ ...prev, metrics: false }))
    }
  }, [mounted, isConnected, user?.id])

  // Handle OAuth callback
  const handleOAuthCallback = useCallback(async (code: string, callbackState: string) => {
    if (!mounted || !user?.id) {
      devLog('Cannot handle callback - not ready')
      return
    }
    
    try {
      setLoading(prev => ({ ...prev, connect: true }))
      setError(null)
      
      devLog('Handling OAuth callback', {
        hasCode: !!code,
        statePreview: callbackState.substring(0, 10) + '...'
      })
      
      // Retrieve stored OAuth data
      const stored = OAuthStorage.retrieve()
      
      // Check if OAuth data is expired
      if (OAuthStorage.isExpired()) {
        throw new TikTokError(
          TikTokErrorType.INVALID_STATE,
          'OAuth session expired - please try connecting again'
        )
      }
      
      // Verify state parameter
      if (callbackState !== stored.state) {
        throw new TikTokError(
          TikTokErrorType.INVALID_STATE,
          'Invalid state parameter - possible CSRF attack',
          { provided: callbackState, stored: stored.state }
        )
      }
      
      // Get the code verifier
      if (!stored.codeVerifier) {
        throw new TikTokError(
          TikTokErrorType.MISSING_CODE_VERIFIER,
          'Missing code verifier - authentication flow was not properly initiated'
        )
      }
      
      const callbackParams = new URLSearchParams({
        code: encodeURIComponent(code),
        state: encodeURIComponent(callbackState),
        user_id: user.id,
        code_verifier: stored.codeVerifier
      })
      
      const response = await TikTokAPIClient.completeAuth(callbackParams)
      
      if (response.success && response.data) {
        setConnectionStatus(response.data)
        setIsConnected(response.data.status === 'active')
        
        devLog('OAuth callback successful', response.data)
        
        // Fetch metrics after successful connection
        if (response.data.status === 'active') {
          await fetchMetrics()
        }
        
        // Clean up stored OAuth data
        OAuthStorage.clear()
      } else {
        throw new TikTokError(
          TikTokErrorType.CALLBACK_FAILED,
          response.error || 'Failed to complete TikTok authentication',
          response
        )
      }
    } catch (err: any) {
      const error = err instanceof TikTokError ? err : new TikTokError(
        TikTokErrorType.CALLBACK_FAILED,
        err.message || 'Failed to complete TikTok authentication',
        err
      )
      setError(error)
      OAuthStorage.clear()
      console.error(error)
    } finally {
      setLoading(prev => ({ ...prev, connect: false }))
    }
  }, [mounted, user?.id, fetchMetrics])

  // Check for OAuth callback parameters
  useEffect(() => {
    if (!mounted || typeof window === 'undefined' || !user?.id) return
    
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const oauthState = urlParams.get('state')
    const oauthError = urlParams.get('error')
    const errorDescription = urlParams.get('error_description')
    
    devLog('Checking for OAuth callback params', {
      hasCode: !!code,
      hasState: !!oauthState,
      hasError: !!oauthError
    })
    
    if (oauthError) {
      setError(new TikTokError(
        TikTokErrorType.AUTH_INIT_FAILED,
        `TikTok OAuth Error: ${oauthError} - ${errorDescription || 'Unknown error'}`,
        { error: oauthError, errorDescription }
      ))
      
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
      return
    }
    
    if (code && oauthState) {
      handleOAuthCallback(code, oauthState)
      
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [mounted, user?.id, handleOAuthCallback])

  // Development mode connection health monitor
  useEffect(() => {
    if (!DEV_MODE || !isConnected) return
    
    const interval = setInterval(() => {
      devLog('Running health check...')
      checkConnectionStatus()
    }, 5 * 60 * 1000) // Every 5 minutes
    
    return () => clearInterval(interval)
  }, [isConnected, checkConnectionStatus])

  // Return safe defaults before mounting
  if (!mounted) {
    return {
      isConnected: false,
      connectionStatus: null,
      metrics: null,
      loading: false,
      error: null,
      connectTikTok: async () => {},
      disconnectTikTok: async () => {},
      refreshConnection: async () => {},
      checkConnectionStatus: async () => {},
      fetchMetrics: async () => {},
    }
  }

  return {
    isConnected,  
    connectionStatus,
    metrics,
    loading: loading.connect || loading.disconnect || loading.sync || loading.checkStatus,
    error,
    connectTikTok,
    disconnectTikTok,
    refreshConnection,
    checkConnectionStatus,
    fetchMetrics,
    syncTikTokVideos: TikTokAPIClient.syncVideos,
    markTikTokDeliverable: TikTokAPIClient.markDeliverable,
    attributeTikTokGMV: TikTokAPIClient.attributeGMV,
    // Dev mode specific exports
    ...(DEV_MODE && {
      _debug: {
        loading,
        clearError: () => setError(null),
        clearOAuthData: () => OAuthStorage.clear(),
        forceRefresh: () => {
          checkConnectionStatus()
          fetchMetrics()
        }
      }
    })
  }
}