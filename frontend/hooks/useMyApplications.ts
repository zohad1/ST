// hooks/useMyApplications.ts
import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'

// Types matching your backend schemas
export interface Application {
  id: string
  creator_id: string
  campaign_id: string
  status: 'pending' | 'approved' | 'rejected' | 'interview' | 'waitlist'
  previous_gmv?: number
  engagement_rate?: number
  application_message?: string
  applied_at: string
  reviewed_at?: string
  reviewer_id?: string
  review_notes?: string
  rejection_reason?: string
  creator?: {
    id: string
    username: string
    first_name?: string
    last_name?: string
    email?: string
    phone?: string
    avatar?: string
    profile_completion?: number
    total_followers?: number
    tiktok_handle?: string
    tiktok_followers?: number
    instagram_handle?: string
    instagram_followers?: number
    youtube_handle?: string
    youtube_followers?: number
    audience_gender?: { male: number; female: number }
    primary_age?: string
    location?: string
    age?: number
    ethnicity?: string
    niche?: string
    shipping_address?: string
  }
  campaign?: {
    id: string
    name: string
    status: string
    description?: string
    brand_name?: string
    brand_logo?: string
    thumbnail_url?: string
    start_date?: string
    end_date?: string
    budget?: number
    min_deliverables_per_creator?: number
    target_gmv?: number
    current_gmv?: number
    category?: string
    type?: string
  }
}

interface ApplicationsResponse {
  applications?: Application[]
  data?: Application[]
  [key: string]: any
}

export function useMyApplications() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMyApplications = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching user applications...')

      const response: ApiResponse<ApplicationsResponse> = await campaignServiceClient.get(
        '/api/v1/applications/my-applications'
      )

      console.log('📡 Applications response:', response)

      if (response.success && response.data) {
        let applicationData: Application[] = []
        
        // Handle different response formats
        if (Array.isArray(response.data)) {
          applicationData = response.data
        } else if (response.data.applications && Array.isArray(response.data.applications)) {
          applicationData = response.data.applications
        } else if (response.data.data && Array.isArray(response.data.data)) {
          applicationData = response.data.data
        }

        console.log('✅ Successfully fetched applications:', applicationData)
        setApplications(applicationData)
      } else {
        const errorMsg = response.error || 'Failed to fetch my applications'
        console.error('❌ Applications fetch failed:', errorMsg)
        setError(errorMsg)
        setApplications([])
      }
    } catch (err: any) {
      console.error('❌ Applications fetch error:', err)
      setError(err.message || 'Unknown error occurred')
      setApplications([])
    } finally {
      setLoading(false)
    }
  }

  // Apply to campaign function (if needed)
  const applyToCampaign = async (applicationData: {
    campaign_id: string
    application_message?: string
    previous_gmv?: number
    engagement_rate?: number
  }): Promise<{ success: boolean; error?: string; data?: Application }> => {
    try {
      console.log('📝 Applying to campaign:', applicationData.campaign_id)
      
      const response: ApiResponse<Application> = await campaignServiceClient.post(
        '/api/v1/applications/',
        {
          campaign_id: applicationData.campaign_id,
          application_data: {
            message: applicationData.application_message,
            previous_gmv: applicationData.previous_gmv,
            engagement_rate: applicationData.engagement_rate
          }
        }
      )

      console.log('📡 Apply response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully applied to campaign')
        // Refresh the applications list
        await fetchMyApplications()
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.error || 'Failed to apply to campaign'
        console.error('❌ Application failed:', errorMsg)
        return { success: false, error: errorMsg }
      }
    } catch (err: any) {
      console.error('💥 Apply error:', err)
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  useEffect(() => {
    fetchMyApplications()
  }, [])

  return {
    applications,
    loading,
    error,
    refetch: fetchMyApplications,
    applyToCampaign
  }
} 