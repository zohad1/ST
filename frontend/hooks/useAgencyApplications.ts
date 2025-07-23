import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'
import { useAuth } from '@/context/authContext'

export interface AgencyApplication {
  id: string
  campaign_id: string
  creator_id: string
  status: "pending" | "approved" | "rejected"
  applied_at: string
  campaign: {
    id: string
    name: string
  }
  creator: {
    id: string
    first_name: string
    last_name: string
    username?: string
    avatar_url?: string
  }
}

export function useAgencyApplications(status?: string) {
  const [applications, setApplications] = useState<AgencyApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, isAuthenticated } = useAuth()

  const fetchAgencyApplications = async () => {
    try {
      setLoading(true)
      setError(null)

      // Don't fetch if not authenticated or not an agency
      if (!isAuthenticated || !user || (user as any).role !== 'agency') {
        console.log('🔒 Not authenticated as agency, skipping applications fetch')
        setApplications([])
        setLoading(false)
        return
      }

      console.log('🚀 [useAgencyApplications] Fetching agency applications...')

      // Build params object
      const params: Record<string, string> = {}
      
      // Add status filter if provided
      if (status && typeof status === 'string' && status !== 'all') {
        params.status = status
      }

      console.log('📋 [useAgencyApplications] Request params:', params)

      // Get all applications for agency's campaigns
      // This endpoint should return applications for campaigns owned by the authenticated agency
      const response = await campaignServiceClient.get('/api/v1/applications/', params)

      console.log('📡 [useAgencyApplications] Response:', response)

      if (response.success && response.data) {
        let applicationData: AgencyApplication[] = []
        
        // Handle different response structures
        const responseData = response.data as any
        if (Array.isArray(responseData)) {
          applicationData = responseData
        } else if (responseData.applications && Array.isArray(responseData.applications)) {
          applicationData = responseData.applications
        } else if (responseData.data && Array.isArray(responseData.data)) {
          applicationData = responseData.data
        }
        
        console.log('✅ [useAgencyApplications] Successfully fetched applications:', applicationData)
        setApplications(applicationData)
      } else {
        const errorMsg = response.error || 'Failed to fetch agency applications'
        console.error('❌ [useAgencyApplications] Fetch failed:', errorMsg)
        setError(errorMsg)
        setApplications([])
      }
    } catch (err: any) {
      console.error('❌ [useAgencyApplications] Error:', err)
      setError(err.message || 'Unknown error occurred')
      setApplications([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgencyApplications()
  }, [status, isAuthenticated, user])

  // Get pending applications count
  const pendingCount = applications.filter(app => app.status === 'pending').length

  return {
    applications,
    pendingCount,
    loading,
    error,
    refetch: fetchAgencyApplications,
  }
} 