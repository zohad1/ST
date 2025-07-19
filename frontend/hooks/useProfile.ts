// hooks/useProfile.ts - User Profile Management Hook
import { useState, useEffect } from 'react'
import { userServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'
import { useAuth } from './useAuth'

export interface UserProfile {
  id: string
  email: string
  username: string
  role: string
  firstName?: string
  lastName?: string
  first_name?: string
  last_name?: string
  full_name?: string
  company_name?: string
  profile_image_url?: string
  bio?: string
  tiktok_handle?: string
  instagram_handle?: string
  discord_handle?: string
  is_active: boolean
  email_verified: boolean
  created_at: string
  phone?: string
  date_of_birth?: string
  gender?: string
  last_login?: string
  // Address fields
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string
  // Creator specific fields
  content_niche?: string
  follower_count?: number
  average_views?: number
  engagement_rate?: number
}

export interface ProfileUpdateData {
  first_name?: string
  last_name?: string
  phone?: string
  date_of_birth?: string
  gender?: string
  bio?: string
  tiktok_handle?: string
  instagram_handle?: string
  discord_handle?: string
  // Address fields
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string
  // Creator specific fields
  content_niche?: string
}

export function useProfile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updating, setUpdating] = useState(false)

  const fetchProfile = async () => {
    if (!user?.id) return

    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching user profile...')

      const response: ApiResponse<any> = await userServiceClient.get('/api/v1/auth/profile')

      console.log('📡 Profile response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully fetched profile:', response.data)
        // Handle the case where the API returns { success: true, data: { profileData } }
        const profileData = response.data.data || response.data
        setProfile(profileData as UserProfile)
      } else {
        const errorMsg = response.error || 'Failed to fetch profile'
        console.error('❌ Profile fetch failed:', errorMsg)
        setError(errorMsg)
      }
    } catch (err: any) {
      console.error('❌ Profile fetch error:', err)
      setError(err.message || 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updateData: ProfileUpdateData): Promise<{ success: boolean; error?: string; data?: UserProfile }> => {
    if (!user?.id) {
      return { success: false, error: 'No user found' }
    }

    try {
      setUpdating(true)
      setError(null)

      console.log('📝 Updating profile:', updateData)
      
      const response: ApiResponse<UserProfile> = await userServiceClient.put(
        '/api/v1/auth/profile',
        updateData
      )

      console.log('📡 Update response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully updated profile')
        setProfile(response.data)
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.error || 'Failed to update profile'
        console.error('❌ Profile update failed:', errorMsg)
        setError(errorMsg)
        return { success: false, error: errorMsg }
      }
    } catch (err: any) {
      console.error('💥 Update error:', err)
      const errorMsg = err.message || 'Unknown error occurred'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setUpdating(false)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [user?.id])

  return {
    profile,
    loading,
    error,
    updating,
    fetchProfile,
    updateProfile
  }
} 