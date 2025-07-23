// hooks/usePerformance.ts - Creator Performance Hook
import { useState, useEffect, useCallback } from 'react'
import { analyticsServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'
import { useAuth } from '@/context/authContext'

export interface CreatorPerformance {
  creator_id: string
  campaign_id?: string
  total_posts: number
  completed_deliverables: number
  on_time_deliverables: number
  total_gmv: string
  avg_views_per_post: string
  avg_engagement_rate: string
  consistency_score: string
  reliability_rating: string
  last_calculated: string
}

export interface PerformanceMetrics {
  total_gmv: string
  total_campaigns: number
  active_campaigns: number
  completed_campaigns: number
  total_posts: number
  avg_engagement_rate: number
  consistency_score: number
  reliability_rating: number
  followers: string
  total_views: number
  total_likes: number
  total_comments: number
  total_shares: number
}

export function usePerformance() {
  const { user } = useAuth()
  const [performance, setPerformance] = useState<CreatorPerformance | null>(null)
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPerformance = useCallback(async (): Promise<void> => {
    console.log('🔍 usePerformance: user?.id =', user?.id)
    console.log('🔍 usePerformance: user =', user)
    
    if (!user?.id) {
      console.log('❌ usePerformance: No user ID available')
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching creator performance for user:', user.id)
      console.log('🚀 Making API call to:', `/api/v1/creators/${user.id}/performance`)
      console.log('🚀 Analytics service client:', analyticsServiceClient)

      // Test health check first
      try {
        const healthResponse = await analyticsServiceClient.get('/health')
        console.log('🏥 Analytics service health check:', healthResponse)
      } catch (healthError) {
        console.error('❌ Analytics service health check failed:', healthError)
      }

      const response: ApiResponse<CreatorPerformance> = await analyticsServiceClient.get(
        `/api/v1/creators/${user.id}/performance`
      )

      console.log('📡 Performance response:', response)
      console.log('📡 Response success:', response.success)
      console.log('📡 Response data:', response.data)
      console.log('📡 Response error:', response.error)
      console.log('📡 Response statusCode:', response.statusCode)

      if (response.success && response.data) {
        console.log('✅ Successfully fetched performance:', response.data)
        setPerformance(response.data)
        
        // Calculate metrics from performance data
        const calculatedMetrics: PerformanceMetrics = {
          total_gmv: response.data.total_gmv || "0.00",
          total_campaigns: 15, // This would come from campaign service
          active_campaigns: 3,
          completed_campaigns: 12,
          total_posts: response.data.total_posts || 0,
          avg_engagement_rate: parseFloat(response.data.avg_engagement_rate || "0.00"),
          consistency_score: parseFloat(response.data.consistency_score || "0.00"),
          reliability_rating: parseFloat(response.data.reliability_rating || "0.0"),
          followers: "25,644", // This would come from user profile
          total_views: 0, // This would be calculated from posts
          total_likes: 0,
          total_comments: 0,
          total_shares: 0,
        }
        
        console.log('📊 Calculated metrics:', calculatedMetrics)
        setMetrics(calculatedMetrics)
      } else {
        const errorMsg = response.error || 'Failed to fetch performance'
        console.error('❌ Performance fetch failed:', errorMsg)
        console.error('❌ Full response:', response)
        setError(errorMsg)
        
        // Set default metrics if no data
        setMetrics({
          total_gmv: "0.00",
          total_campaigns: 0,
          active_campaigns: 0,
          completed_campaigns: 0,
          total_posts: 0,
          avg_engagement_rate: 0,
          consistency_score: 0,
          reliability_rating: 0,
          followers: "0",
          total_views: 0,
          total_likes: 0,
          total_comments: 0,
          total_shares: 0,
        })
      }
    } catch (err: any) {
      console.error('❌ Performance fetch error:', err)
      console.error('❌ Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      })
      setError(err.message || 'Unknown error occurred')
      
      // Set default metrics on error
      setMetrics({
        total_gmv: "0.00",
        total_campaigns: 0,
        active_campaigns: 0,
        completed_campaigns: 0,
        total_posts: 0,
        avg_engagement_rate: 0,
        consistency_score: 0,
        reliability_rating: 0,
        followers: "0",
        total_views: 0,
        total_likes: 0,
        total_comments: 0,
        total_shares: 0,
      })
    } finally {
      setLoading(false)
    }
  }, [user?.id])

  useEffect(() => {
    fetchPerformance()
  }, [fetchPerformance])

  return {
    performance,
    metrics,
    loading,
    error,
    fetchPerformance
  }
} 