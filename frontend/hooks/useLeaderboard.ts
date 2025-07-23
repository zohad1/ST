import { useState, useEffect } from 'react'
import { analyticsServiceClient } from '@/lib/api/client'

export interface LeaderboardEntry {
  rank: number
  name: string
  avatar: string
  gmv: number
  badge: string
  isCurrentUser?: boolean
}

export function useLeaderboard() {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true)
        setError(null)
        
        console.log('🔍 [useLeaderboard] Fetching leaderboard data...')
        
        const response = await analyticsServiceClient.get('/api/v1/analytics/leaderboard')
        
        if (response.success && response.data) {
          console.log('✅ [useLeaderboard] Leaderboard data received:', response.data)
          
          // Transform backend data to match component expectations
          const responseData = response.data as any
          const dataArray = Array.isArray(responseData) ? responseData : 
                           (responseData?.leaderboard || responseData?.data || [])
          
          const transformedData = dataArray.map((entry: any, index: number) => ({
            rank: index + 1,
            name: entry.creator_name || entry.name || 'Unknown Creator',
            avatar: entry.avatar || entry.profile_image || '/placeholder.svg?height=40&width=40',
            gmv: entry.total_gmv || entry.gmv || 0,
            badge: getBadgeForGMV(entry.total_gmv || entry.gmv || 0),
            isCurrentUser: entry.is_current_user || false,
          }))
          
          setLeaderboardData(transformedData)
        } else {
          console.error('❌ [useLeaderboard] Failed to fetch leaderboard:', response.error)
          setError(response.error || 'Failed to fetch leaderboard data')
          
          // Fallback to empty array if API fails
          setLeaderboardData([])
        }
      } catch (err: any) {
        console.error('❌ [useLeaderboard] Error fetching leaderboard:', err)
        setError(err.message || 'Failed to fetch leaderboard data')
        setLeaderboardData([])
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboard()
  }, [])

  return {
    leaderboardData,
    loading,
    error,
  }
}

// Helper function to determine badge based on GMV
function getBadgeForGMV(gmv: number): string {
  if (gmv >= 10000) return '$10K+'
  if (gmv >= 5000) return '$5K-$10K'
  if (gmv >= 1000) return '$1K-$5K'
  return '<$1K'
} 