// hooks/useCreatorAcceptedCampaigns.ts
import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'

// Campaign type definition
export interface AcceptedCampaign {
  id: string
  name: string
  description?: string
  brand_id: string
  brand_name?: string
  brand_logo?: string
  agency_id: string
  status: 'active' | 'completed' | 'paused'
  start_date: string
  end_date: string
  budget?: number
  category?: string
  current_gmv?: number
  gmv_target?: number
  completed_deliverables?: number
  total_deliverables?: number
  created_at: string
  updated_at: string
  application_status: 'approved'
  application_id: string
}

interface AcceptedCampaignsResponse {
  campaigns?: AcceptedCampaign[]
  data?: AcceptedCampaign[]
  [key: string]: any
}

export function useCreatorAcceptedCampaigns() {
  const [campaigns, setCampaigns] = useState<AcceptedCampaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAcceptedCampaigns = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching creator accepted campaigns...')

      // First, get the creator's approved applications
      const applicationsResponse: ApiResponse<any> = await campaignServiceClient.get(
        '/api/v1/applications/my-applications'
      )

      if (!applicationsResponse.success || !applicationsResponse.data) {
        console.log('❌ Failed to fetch applications or no applications found')
        setCampaigns([])
        setLoading(false)
        return
      }

      // Extract approved applications
      let applications: any[] = []
      if (Array.isArray(applicationsResponse.data)) {
        applications = applicationsResponse.data
      } else if (applicationsResponse.data.applications) {
        applications = applicationsResponse.data.applications
      } else if (applicationsResponse.data.data) {
        applications = applicationsResponse.data.data
      }

      // Filter for approved applications only
      const approvedApplications = applications.filter(app => app.status === 'approved')
      
      console.log('✅ Found approved applications:', approvedApplications.length)

      if (approvedApplications.length === 0) {
        setCampaigns([])
        setLoading(false)
        return
      }

      // Get campaign details for each approved application
      const campaignPromises = approvedApplications.slice(0, 4).map(async (application) => {
        try {
          const campaignResponse: ApiResponse<any> = await campaignServiceClient.get(
            `/api/v1/campaigns/${application.campaign_id}`
          )

          if (campaignResponse.success && campaignResponse.data) {
            return {
              ...campaignResponse.data,
              application_status: 'approved',
              application_id: application.id
            }
          }
          return null
        } catch (err) {
          console.error(`❌ Failed to fetch campaign ${application.campaign_id}:`, err)
          return null
        }
      })

      const campaignResults = await Promise.all(campaignPromises)
      const validCampaigns = campaignResults.filter(campaign => campaign !== null)

      console.log('✅ Successfully fetched accepted campaigns:', validCampaigns.length)
      setCampaigns(validCampaigns)

    } catch (err: any) {
      console.error('❌ Accepted campaigns fetch error:', err)
      setError(err.message || 'Unknown error occurred')
      setCampaigns([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAcceptedCampaigns()
  }, [])

  return {
    campaigns,
    loading,
    error,
    refetch: fetchAcceptedCampaigns
  }
} 