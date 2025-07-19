"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { userServiceClient } from "@/lib/api/client"
import { ENDPOINTS } from "@/lib/api/config"
import type { User } from "@/lib/types/api"

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  username: string
  role: "creator" | "agency" | "brand"
}

interface EmailVerificationData {
  token: string
}

interface ForgotPasswordData {
  email: string
}

interface ResetPasswordData {
  token: string
  new_password: string
}

// Helper function to get dashboard URL based on user role
const getDashboardUrl = (role: string): string => {
  switch (role) {
    case "creator":
      return "/creator-dashboard"
    case "agency":
      return "/agency-dashboard"
    case "brand":
      return "/client-dashboard"
    default:
      return "/dashboard"
  }
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  })

  const router = useRouter()

  // Helper function to store tokens in multiple locations
  const storeTokens = (accessToken: string, refreshToken?: string) => {
    console.log("💾 Storing tokens in localStorage and sessionStorage")
    
    // Store in localStorage
    localStorage.setItem("auth_token", accessToken)
    localStorage.setItem("access_token", accessToken)
    
    // Store in sessionStorage for current session
    sessionStorage.setItem("auth_token", accessToken)
    sessionStorage.setItem("access_token", accessToken)
    
    if (refreshToken) {
      localStorage.setItem("refresh_token", refreshToken)
      sessionStorage.setItem("refresh_token", refreshToken)
    }
    
    // Verify storage
    console.log("✅ Tokens stored verification:", {
      localStorage_auth: !!localStorage.getItem("auth_token"),
      localStorage_access: !!localStorage.getItem("access_token"),
      sessionStorage_auth: !!sessionStorage.getItem("auth_token"),
      sessionStorage_access: !!sessionStorage.getItem("access_token")
    })
  }

  // Helper function to clear all tokens
  const clearTokens = () => {
    console.log("🗑️ Clearing all tokens")
    localStorage.removeItem("auth_token")
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    sessionStorage.removeItem("auth_token")
    sessionStorage.removeItem("access_token")
    sessionStorage.removeItem("refresh_token")
  }

  // Helper function to refresh access token
  const refreshAccessToken = async (): Promise<boolean> => {
    console.log("🔄 Attempting to refresh access token...")
    const refreshToken = localStorage.getItem("refresh_token") || sessionStorage.getItem("refresh_token")
    
    if (!refreshToken) {
      console.log("❌ No refresh token available")
      return false
    }

    try {
      const response = await userServiceClient.post<{
        access_token: string
        refresh_token?: string
      }>('/api/v1/auth/refresh', { refresh_token: refreshToken })

      if (response.success && response.data) {
        const { access_token, refresh_token: newRefreshToken } = response.data
        storeTokens(access_token, newRefreshToken)
        console.log("✅ Token refreshed successfully")
        return true
      }
    } catch (error) {
      console.error("❌ Token refresh failed:", error)
    }

    return false
  }

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      console.log("🔐 [useAuth] Initializing auth state...")
      
      const token = localStorage.getItem("auth_token") || 
                   localStorage.getItem("access_token") ||
                   sessionStorage.getItem("auth_token") ||
                   sessionStorage.getItem("access_token")
      
      console.log("🔍 [useAuth] Token check:", {
        hasToken: !!token,
        tokenPreview: token ? token.substring(0, 20) + "..." : null,
        source: token ? (
          localStorage.getItem("auth_token") ? "localStorage.auth_token" :
          localStorage.getItem("access_token") ? "localStorage.access_token" :
          sessionStorage.getItem("auth_token") ? "sessionStorage.auth_token" :
          sessionStorage.getItem("access_token") ? "sessionStorage.access_token" : "unknown"
        ) : "none"
      })
      
      if (!token) {
        console.log("❌ [useAuth] No token found, user is not authenticated")
        setState((prev) => ({ ...prev, isLoading: false, isAuthenticated: false, user: null }))
        return
      }

      try {
        console.log("📡 [useAuth] Fetching user profile with token...")
        
        // Try to fetch user profile - first attempt with current endpoint
        let response = await userServiceClient.get<User>(ENDPOINTS.AUTH.PROFILE)
        
        // If that fails, try the /me endpoint which is common in FastAPI
        if (!response.success) {
          console.log("📡 [useAuth] Trying /me endpoint...")
          response = await userServiceClient.get<User>('/api/v1/me')
        }
        
        // If still failing and it's a 401, try to refresh token
        if (!response.success && response.error?.includes('401')) {
          console.log("🔄 [useAuth] Got 401, attempting token refresh...")
          const refreshed = await refreshAccessToken()
          
          if (refreshed) {
            // Retry with new token
            response = await userServiceClient.get<User>(ENDPOINTS.AUTH.PROFILE)
            if (!response.success) {
              response = await userServiceClient.get<User>('/api/v1/me')
            }
          }
        }
        
        console.log("📡 [useAuth] Profile response:", response)
        
        if (response.success && response.data) {
          // Handle nested data structure
          const userData = ((response.data && typeof response.data === 'object' && 'data' in response.data) 
            ? response.data.data 
            : response.data) as User
          
          console.log("✅ [useAuth] User authenticated:", {
            id: userData.id,
            email: userData.email,
            role: userData.role
          })
          
          setState({
            user: userData,
            isLoading: false,
            isAuthenticated: true,
            error: null,
          })
        } else {
          console.log("❌ [useAuth] Invalid profile response, clearing tokens")
          clearTokens()
          setState({
            user: null,
            isLoading: false,
            isAuthenticated: false,
            error: "Failed to load user profile"
          })
        }
      } catch (error) {
        console.error("❌ [useAuth] Auth initialization error:", error)
          clearTokens()
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: "Failed to initialize authentication"
        })
      }
    }

    initAuth()
  }, [])

  // Listen for storage changes (for multi-tab logout)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "auth_token" || e.key === "access_token") {
        if (!e.newValue) {
          console.log("🔄 [useAuth] Token cleared in another tab, logging out")
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
            error: null,
          })
        }
      }
    }

    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [])

  // Login function
  const login = async (credentials: LoginCredentials): Promise<{ success: boolean; error?: string }> => {
    console.log("🔐 [useAuth] Attempting login...")
    
    try {
      const response = await userServiceClient.post<{
        data?: {
          access_token: string
          refresh_token?: string
          user: User
        }
        access_token?: string
        refresh_token?: string
        user?: User
      }>(ENDPOINTS.AUTH.LOGIN, credentials)

      if (response.success && response.data) {
        console.log("✅ [useAuth] Login successful, processing response...")
        
        // Handle nested response structure
        const responseData = response.data?.data || response.data
        console.log("🔍 [useAuth] Actual response data:", responseData)
        
        const { access_token, refresh_token, user } = responseData || {}
        
        // Handle different token field names
        const actualAccessToken = access_token
        const actualRefreshToken = refresh_token
        
        console.log("🔍 [useAuth] User object:", user)
        console.log("🔍 [useAuth] User role:", user?.role)
        console.log("🔍 [useAuth] Access token:", actualAccessToken ? "Present" : "Missing")
        console.log("🔍 [useAuth] Token keys in response:", Object.keys(responseData))
        
        if (!actualAccessToken) {
          console.error("❌ [useAuth] No access token found in response")
          return { success: false, error: "No access token received" }
        }
        
        storeTokens(actualAccessToken, actualRefreshToken)
        
        console.log("💾 [useAuth] Setting user state:", user)
        
        // Set authentication state immediately but with a flag to prevent immediate redirects
        setState({
          user: user || null,
          isLoading: false,
          isAuthenticated: true,
          error: null,
        })
        
        console.log("✅ [useAuth] Login successful, state will update shortly...")
        
        return { success: true }
      } else {
        const error = response.error || "Login failed"
        console.error("❌ [useAuth] Login failed:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Login error:", error)
      return { success: false, error: error.message || "Login failed" }
    }
  }

  // Register function - Updated to handle email verification
  const register = async (data: RegisterData): Promise<{ success: boolean; error?: string; requires_verification?: boolean }> => {
    console.log("📝 [useAuth] Attempting registration...")
    
    try {
      const response = await userServiceClient.post<{
        message: string
        success: boolean
      }>('/api/v1/auth/signup', data)

      if (response.success && response.data) {
        console.log("✅ [useAuth] Registration successful, verification email sent")
          return { success: true, requires_verification: true }
      } else {
        const error = response.error || "Registration failed"
        console.error("❌ [useAuth] Registration failed:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Registration error:", error)
      return { success: false, error: error.message || "Registration failed" }
    }
  }

  // Verify email function
  const verifyEmail = async (data: EmailVerificationData): Promise<{ success: boolean; error?: string }> => {
    console.log("📧 [useAuth] Verifying email...")
    
    try {
      const response = await userServiceClient.post<{
        message: string
        success: boolean
      }>('/api/v1/auth/verify-email', data)

      if (response.success && response.data) {
        console.log("✅ [useAuth] Email verified successfully")
        return { success: true }
      } else {
        const error = response.error || "Email verification failed"
        console.error("❌ [useAuth] Email verification failed:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Email verification error:", error)
      return { success: false, error: error.message || "Email verification failed" }
    }
  }

  // Resend verification email function
  const resendVerification = async (email: string): Promise<{ success: boolean; error?: string }> => {
    console.log("📧 [useAuth] Resending verification email...")
    
    try {
      const response = await userServiceClient.post<{
        message: string
        success: boolean
      }>('/api/v1/auth/resend-verification', { email })

      if (response.success && response.data) {
        console.log("✅ [useAuth] Verification email resent successfully")
        return { success: true }
      } else {
        const error = response.error || "Failed to resend verification email"
        console.error("❌ [useAuth] Failed to resend verification email:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Resend verification error:", error)
      return { success: false, error: error.message || "Failed to resend verification email" }
    }
  }

  // Forgot password function
  const forgotPassword = async (data: ForgotPasswordData): Promise<{ success: boolean; error?: string }> => {
    console.log("🔐 [useAuth] Sending password reset email...")
    
    try {
      const response = await userServiceClient.post<{
        message: string
        success: boolean
      }>('/api/v1/auth/forgot-password', data)

      if (response.success && response.data) {
        console.log("✅ [useAuth] Password reset email sent successfully")
        return { success: true }
      } else {
        const error = response.error || "Failed to send password reset email"
        console.error("❌ [useAuth] Failed to send password reset email:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Forgot password error:", error)
      return { success: false, error: error.message || "Failed to send password reset email" }
    }
  }

  // Reset password function
  const resetPassword = async (data: ResetPasswordData): Promise<{ success: boolean; error?: string }> => {
    console.log("🔐 [useAuth] Resetting password...")
    
    try {
      const response = await userServiceClient.post<{
        message: string
        success: boolean
      }>('/api/v1/auth/reset-password', data)

      if (response.success && response.data) {
        console.log("✅ [useAuth] Password reset successfully")
        return { success: true }
      } else {
        const error = response.error || "Password reset failed"
        console.error("❌ [useAuth] Password reset failed:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Reset password error:", error)
      return { success: false, error: error.message || "Password reset failed" }
    }
  }

  // Logout function
  const logout = useCallback(async (): Promise<void> => {
    console.log("🚪 [useAuth] Logging out...")
    
    try {
      // Call logout endpoint if available
      await userServiceClient.post(ENDPOINTS.AUTH.LOGOUT)
    } catch (error) {
      console.warn("⚠️ [useAuth] Logout endpoint failed, continuing with local cleanup")
    }
    
    clearTokens()
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,
    })
    
    console.log("✅ [useAuth] Logout successful")
    router.push('/auth/login')
  }, [router])

  // Update user profile
  const updateProfile = async (profileData: Partial<User>): Promise<{ success: boolean; error?: string }> => {
    console.log("📝 [useAuth] Updating profile...")
    
    try {
      const response = await userServiceClient.put<User>(ENDPOINTS.USERS.UPDATE_PROFILE, profileData)
      
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          user: response.data!
        }))
        
        console.log("✅ [useAuth] Profile updated successfully")
        return { success: true }
      } else {
        const error = response.error || "Profile update failed"
        console.error("❌ [useAuth] Profile update failed:", error)
        return { success: false, error }
      }
    } catch (error: any) {
      console.error("❌ [useAuth] Profile update error:", error)
      return { success: false, error: error.message || "Profile update failed" }
    }
  }

  // Refresh user data
  const refreshUser = useCallback(async (): Promise<void> => {
    console.log("🔄 [useAuth] Refreshing user data...")
    
    try {
      const response = await userServiceClient.get<User>(ENDPOINTS.AUTH.PROFILE)
      
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          user: response.data!
        }))
        console.log("✅ [useAuth] User data refreshed")
      }
    } catch (error) {
      console.error("❌ [useAuth] Failed to refresh user data:", error)
    }
  }, [])

  // Clear error function
  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null
    }))
  }, [])

  return {
    // State
    user: state.user,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
    error: state.error,
    
    // Actions
    login,
    register,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    logout,
    updateProfile,
    refreshUser,
    clearError,
  }
}
