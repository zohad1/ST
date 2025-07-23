// hooks/useCampaigns.ts - Complete campaigns hook

import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'

// Campaign type definition
export interface Campaign {
  id: string
  name: string
  description?: string
  brand_id: string
  brand_name?: string
  brand_logo?: string
  agency_id: string
  status: 'draft' | 'active' | 'paused' | 'completed'
  start_date: string
  end_date: string
  budget?: number
  category?: string
  visibility?: string
  min_followers?: number
  current_gmv?: number
  gmv_target?: number
  completed_deliverables?: number
  total_deliverables?: number
  created_at: string
  updated_at: string
}

interface CampaignListResponse {
  campaigns: Campaign[]
  total: number
  limit: number
  offset: number
}

interface CampaignFilters {
  search?: string
  category?: string
  payoutType?: string
  status?: string
  limit?: number
  offset?: number
}

// Main hook for fetching campaigns
export function useCampaigns(filters: CampaignFilters = {}) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCampaigns = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching campaigns...')

      // Build params object with defaults
      const params: Record<string, string | number> = { 
        limit: filters.limit || 20, 
        offset: filters.offset || 0 
      }
      
      // Add filter parameters only if they exist and aren't empty
      if (filters.status && filters.status !== 'all') params.status = filters.status
      if (filters.search && typeof filters.search === 'string' && filters.search.trim()) params.search = filters.search.trim()
      if (filters.category && filters.category !== 'all') params.category = filters.category
      if (filters.payoutType && filters.payoutType !== 'all') params.payout_type = filters.payoutType

      console.log('📋 Request params:', params)

      // Use the correct endpoint
      const response: ApiResponse<CampaignListResponse | Campaign[]> = await campaignServiceClient.get(
        '/api/v1/campaigns',
        params
      )

      console.log('📡 Campaigns response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully fetched campaigns:', response.data)
        
        // Handle both response formats: direct array or object with campaigns property
        if (Array.isArray(response.data)) {
          setCampaigns(response.data)
        } else if (response.data && 'campaigns' in response.data) {
          setCampaigns(response.data.campaigns)
        } else {
          console.error('❌ Unexpected response format:', response.data)
          setError('Unexpected response format')
          setCampaigns([])
        }
      } else {
        const errorMsg = response.error || 'Failed to fetch campaigns'
        console.error('❌ Campaigns fetch failed:', errorMsg)
        setError(errorMsg)
        setCampaigns([])
      }
    } catch (err: any) {
      console.error("❌ Campaigns fetch error:", err)
      setError(err.message || 'Unknown error occurred')
      setCampaigns([])
    } finally {
      setLoading(false)
    }
  }

  const createCampaign = async (campaignData: Partial<Campaign>) => {
    try {
      const response: ApiResponse<Campaign> = await campaignServiceClient.post(
        '/api/v1/campaigns',
        campaignData
      )

      if (response.success && response.data) {
        setCampaigns(prev => [...prev, response.data!])
        return { success: true, data: response.data }
      } else {
        return { success: false, error: response.error || 'Failed to create campaign' }
      }
    } catch (err: any) {
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  const updateCampaign = async (id: string, campaignData: Partial<Campaign>) => {
    try {
      const response: ApiResponse<Campaign> = await campaignServiceClient.put(
        `/api/v1/campaigns/${id}`,
        campaignData
      )

      if (response.success && response.data) {
        setCampaigns(prev => 
          prev.map(campaign => 
            campaign.id === id ? response.data! : campaign
          )
        )
        return { success: true, data: response.data }
      } else {
        return { success: false, error: response.error || 'Failed to update campaign' }
      }
    } catch (err: any) {
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  const deleteCampaign = async (id: string) => {
    try {
      const response: ApiResponse<any> = await campaignServiceClient.delete(`/api/v1/campaigns/${id}`)

      if (response.success) {
        setCampaigns(prev => prev.filter(campaign => campaign.id !== id))
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Failed to delete campaign' }
      }
    } catch (err: any) {
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  // Apply to a campaign
  const applyCampaign = async (campaignId: string) => {
    try {
      console.log('📝 Applying to campaign:', campaignId)
      
      const response: ApiResponse<any> = await campaignServiceClient.post(
        `/api/v1/campaigns/${campaignId}/apply`,
        {}
      )

      console.log('📡 Apply campaign response:', response)

      if (response.success) {
        console.log('✅ Successfully applied to campaign')
        return { success: true }
      } else {
        const errorMsg = response.error || 'Failed to apply to campaign'
        console.error('❌ Campaign application failed:', errorMsg)
        return { success: false, error: errorMsg }
      }
    } catch (err: any) {
      console.error('💥 Apply campaign error:', err)
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  // Fetch campaigns on component mount and when dependencies change
  useEffect(() => {
    fetchCampaigns()
  }, [filters.status, filters.search, filters.category, filters.payoutType, filters.limit, filters.offset])

  return {
    campaigns,
    loading,
    error,
    refetch: fetchCampaigns,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    applyCampaign
  }
}

// Hook for fetching a single campaign
export function useCampaign(id: string) {
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCampaign = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<Campaign> = await campaignServiceClient.get(`/api/v1/campaigns/${id}`)

      if (response.success && response.data) {
        setCampaign(response.data)
      } else {
        setError(response.error || 'Failed to fetch campaign')
      }
    } catch (err: any) {
      setError(err.message || 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) {
      fetchCampaign()
    }
  }, [id])

  return {
    campaign,
    loading,
    error,
    refetch: fetchCampaign
  }
}

// Hook for campaign applications
export function useCampaignApplications(campaignId: string) {
  const [applications, setApplications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchApplications = async () => {
    try {
      setLoading(true)
      setError(null)

      const response: ApiResponse<any[]> = await campaignServiceClient.get(
        `/api/v1/applications/campaign/${campaignId}`
      )

      if (response.success && response.data) {
        setApplications(response.data)
      } else {
        setError(response.error || 'Failed to fetch applications')
      }
    } catch (err: any) {
      setError(err.message || 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const approveApplication = async (applicationId: string) => {
    try {
      const response: ApiResponse<any> = await campaignServiceClient.post(
        `/api/v1/applications/${applicationId}/review`,
        { status: 'approved' }
      )

      if (response.success) {
        await fetchApplications() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Failed to approve application' }
      }
    } catch (err: any) {
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  const rejectApplication = async (applicationId: string, reason?: string) => {
    try {
      const response: ApiResponse<any> = await campaignServiceClient.post(
        `/api/v1/applications/${applicationId}/review`,
        { status: 'rejected', reason }
      )

      if (response.success) {
        await fetchApplications() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Failed to reject application' }
      }
    } catch (err: any) {
      return { success: false, error: err.message || 'Unknown error occurred' }
    }
  }

  useEffect(() => {
    if (campaignId) {
      fetchApplications()
    }
  }, [campaignId])

  return {
    applications,
    loading,
    error,
    refetch: fetchApplications,
    approveApplication,
    rejectApplication
  }
}
