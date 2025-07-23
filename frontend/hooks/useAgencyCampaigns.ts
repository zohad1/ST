import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'
import { useAuth } from '@/context/authContext'

export interface AgencyCampaign {
  id: string
  name: string
  description?: string
  status: "draft" | "active" | "paused" | "completed" | "cancelled"
  type: string
  budget?: number
  target_gmv?: number
  current_gmv?: number
  target_creators?: number
  current_creators?: number
  target_posts?: number
  current_posts?: number
  total_views?: number
  total_engagement?: number
  start_date?: string
  end_date?: string
  created_at: string
  updated_at: string
}

export function useAgencyCampaigns(
  status?: string,
  limit: number = 20,
  offset: number = 0
) {
  const [campaigns, setCampaigns] = useState<AgencyCampaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, isAuthenticated } = useAuth()

  const fetchAgencyCampaigns = async () => {
    try {
      setLoading(true)
      setError(null)

      // Don't fetch if not authenticated or not an agency
      if (!isAuthenticated || !user || (user as any).role !== 'agency') {
        console.log('🔒 Not authenticated as agency, skipping fetch')
        setCampaigns([])
        setLoading(false)
        return
      }

      console.log('🚀 [useAgencyCampaigns] Fetching agency campaigns...')

      // Build params object
      const params: Record<string, string | number> = { 
        limit, 
        offset 
      }
      
      // Add status filter if provided
      if (status && typeof status === 'string' && status !== 'all') {
        params.status = status
      }

      console.log('📋 [useAgencyCampaigns] Request params:', params)

      // Use the campaigns endpoint which should filter by agency
      const response = await campaignServiceClient.get('/api/v1/campaigns', params)

      console.log('📡 [useAgencyCampaigns] Response:', response)

      if (response.success && response.data) {
        let campaignData: AgencyCampaign[] = []
        
        // Handle different response structures
        const responseData = response.data as any
        if (Array.isArray(responseData)) {
          campaignData = responseData
        } else if (responseData.campaigns && Array.isArray(responseData.campaigns)) {
          campaignData = responseData.campaigns
        } else if (responseData.data && Array.isArray(responseData.data)) {
          campaignData = responseData.data
        }
        
        console.log('✅ [useAgencyCampaigns] Successfully fetched campaigns:', campaignData)
        setCampaigns(campaignData)
      } else {
        const errorMsg = response.error || 'Failed to fetch agency campaigns'
        console.error('❌ [useAgencyCampaigns] Fetch failed:', errorMsg)
        setError(errorMsg)
        setCampaigns([])
      }
    } catch (err: any) {
      console.error('❌ [useAgencyCampaigns] Error:', err)
      setError(err.message || 'Unknown error occurred')
      setCampaigns([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgencyCampaigns()
  }, [status, limit, offset, isAuthenticated, user])

  return {
    campaigns,
    loading,
    error,
    refetch: fetchAgencyCampaigns,
  }
} 