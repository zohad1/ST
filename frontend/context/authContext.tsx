'use client'

import { createContext, useContext, useState, useEffect, ReactNode, ComponentType } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string;
  email: string;
  username: string;
  role: 'creator' | 'agency' | 'brand' | 'admin';
  display_name: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  email_verified: boolean;
  is_active: boolean;
  profile_completion_percentage: number;
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<any>
  logout: () => void
  refreshUser: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_URL = 'http://localhost:8000/api/v1'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  // Prevent SSR issues
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          setLoading(false)
          return
        }

        // Validate token and get user - use a safe endpoint
        try {
          const response = await fetch(`${API_URL}/auth/profile`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })

          if (response.ok) {
            const data = await response.json()
            // Handle nested response structure
            const userData = data.data || data
            setUser(userData)
          } else {
            // Token invalid, clear it
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
          }
        } catch (fetchError) {
          // Network error or server down - clear tokens
          console.warn('Auth initialization failed:', fetchError)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [mounted])

  const login = async (email: string, password: string) => {
    setError(null)
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()

      if (response.ok) {
        // Handle nested response structure
        const responseData = data.data || data
        localStorage.setItem('access_token', responseData.access_token)
        if (responseData.refresh_token) {
          localStorage.setItem('refresh_token', responseData.refresh_token)
        }
        setUser(responseData.user)
        return { success: true, user: responseData.user }
      } else {
        const errorMessage = data.detail || data.message || 'Login failed'
        setError(errorMessage)
        return { success: false, error: errorMessage }
      }
    } catch (error) {
      const errorMessage = 'Network error - please check your connection'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    setError(null)
    router.push('/auth/login')
  }

  const refreshUser = async () => {
    if (!mounted) return
    
    const token = localStorage.getItem('access_token')
    if (!token) return

    try {
      const response = await fetch(`${API_URL}/auth/profile`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        const userData = data.data || data
        setUser(userData)
      }
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  }

  const clearError = () => {
    setError(null)
  }

  const value = {
    user,
    isAuthenticated: !!user,
    loading: !mounted || loading,
    error,
    login,
    logout,
    refreshUser,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// ===== ADD THIS: withAuth Higher-Order Component =====

interface WithAuthOptions {
  requiredRole?: string | string[]
  redirectTo?: string
  requireEmailVerified?: boolean
}

export function withAuth<P extends {}>(
  WrappedComponent: ComponentType<P>,
  options: WithAuthOptions = {}
) {
  const {
    requiredRole,
    redirectTo = '/auth/login',
    requireEmailVerified = true
  } = options

  return function AuthenticatedComponent(props: P) {
    const { user, isAuthenticated, loading } = useAuth()
    const router = useRouter()
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
      setMounted(true)
    }, [])

    useEffect(() => {
      if (!mounted || loading) return

      // Check if user is authenticated
      if (!isAuthenticated || !user) {
        console.log('🔒 User not authenticated, redirecting to:', redirectTo)
        router.push(redirectTo)
        return
      }

      // Check email verification if required
      if (requireEmailVerified && !user.email_verified) {
        console.log('⚠️ Email not verified, redirecting to verification')
        router.push(`/auth/verification?email=${encodeURIComponent(user.email)}`)
        return
      }

      // Check role if specified
      if (requiredRole) {
        const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
        if (!roles.includes(user.role)) {
          console.log(`🚫 User role '${user.role}' not authorized. Required: ${roles.join(', ')}`)
          router.push('/unauthorized')
          return
        }
      }
    }, [mounted, isAuthenticated, user, loading, router])

    // Show loading during SSR and authentication check
    if (!mounted || loading) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-background">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="text-muted-foreground">Authenticating...</p>
          </div>
        </div>
      )
    }

    // Don't render anything while redirecting
    if (!isAuthenticated || !user) {
      return null
    }

    // Check email verification
    if (requireEmailVerified && !user.email_verified) {
      return null
    }

    // Check role authorization
    if (requiredRole) {
      const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
      if (!roles.includes(user.role)) {
        return null
      }
    }

    // All checks passed, render the component
    return <WrappedComponent {...props} />
  }
}