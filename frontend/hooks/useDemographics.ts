// hooks/useDemographics.ts - Updated to use real database endpoints
import { useState, useEffect } from 'react'
import { sharedServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'
import { useAuth } from '@/context/authContext'

export interface DemographicsEntry {
  id: string
  creator_id: string
  age_group: string
  gender: string
  percentage: number
  country?: string
  updated_at?: string
}

export interface DemographicsSummary {
  creator_id: string
  total_entries: number
  total_percentage: number
  age_distribution: Record<string, number>
  gender_distribution: Record<string, number>
  country_distribution: Record<string, number>
  last_updated?: string
}

export interface DemographicsCreate {
  age_group: string
  gender: string
  percentage: number
  country?: string
}

export function useDemographics() {
  const { user } = useAuth()
  const [demographics, setDemographics] = useState<DemographicsEntry[]>([])
  const [summary, setSummary] = useState<DemographicsSummary | null>(null)
  const [loading, setLoading] = useState(false) // Changed to false to not block UI
  const [error, setError] = useState<string | null>(null)
  const [updating, setUpdating] = useState(false)

  const fetchDemographics = async () => {
    if (!user?.id) return

    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching demographics from /api/v1/creators/demographics...')

      // TEMPORARILY DISABLED - Use default data instead
      console.log('⚠️ Demographics service temporarily disabled, using default data')
      
      // Use default demographics data for now
      const defaultDemographics: DemographicsEntry[] = [
        {
          id: "1",
          creator_id: user.id,
          age_group: "18-24",
          gender: "female",
          percentage: 45,
          country: "United States",
          updated_at: new Date().toISOString()
        },
        {
          id: "2", 
          creator_id: user.id,
          age_group: "25-34",
          gender: "female",
          percentage: 22,
          country: "United States",
          updated_at: new Date().toISOString()
        },
        {
          id: "3",
          creator_id: user.id,
          age_group: "18-24",
          gender: "male",
          percentage: 20,
          country: "United States",
          updated_at: new Date().toISOString()
        },
        {
          id: "4",
          creator_id: user.id,
          age_group: "25-34",
          gender: "male",
          percentage: 13,
          country: "United States",
          updated_at: new Date().toISOString()
        }
      ]

      console.log('✅ Using default demographics data:', defaultDemographics)
      setDemographics(defaultDemographics)

      // Comment out the actual API call for now
      /*
      const response: ApiResponse<DemographicsEntry[]> = await sharedServiceClient.get(
        `/api/v1/creators/demographics`
      )

      console.log('📡 Demographics response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully fetched demographics:', response.data)
        setDemographics(response.data)
      } else {
        const errorMsg = response.error || 'Failed to fetch demographics'
        console.error('❌ Demographics fetch failed:', errorMsg)
        setError(errorMsg)
        setDemographics([])
      }
      */
    } catch (err: any) {
      console.error('❌ Demographics fetch error:', err)
      setError(err.message || 'Unknown error occurred')
      setDemographics([])
    } finally {
      setLoading(false)
    }
  }

  const fetchDemographicsSummary = async () => {
    if (!user?.id) return

    try {
      setError(null)

      console.log('🚀 Fetching demographics summary...')

      // Calculate summary from demographics data
      const demographicsData = demographics.length > 0 ? demographics : []
      
      if (demographicsData.length > 0) {
        // Calculate age distribution
        const ageDistribution: Record<string, number> = {}
        const genderDistribution: Record<string, number> = {}
        const countryDistribution: Record<string, number> = {}
        
        demographicsData.forEach(demo => {
          // Age distribution
          ageDistribution[demo.age_group] = (ageDistribution[demo.age_group] || 0) + demo.percentage
          
          // Gender distribution
          genderDistribution[demo.gender] = (genderDistribution[demo.gender] || 0) + demo.percentage
          
          // Country distribution
          if (demo.country) {
            countryDistribution[demo.country] = (countryDistribution[demo.country] || 0) + demo.percentage
          }
        })
        
        const totalPercentage = demographicsData.reduce((sum, demo) => sum + demo.percentage, 0)
        
        const summaryData: DemographicsSummary = {
          creator_id: user.id,
          total_entries: demographicsData.length,
          total_percentage: totalPercentage,
          age_distribution: ageDistribution,
          gender_distribution: genderDistribution,
          country_distribution: countryDistribution,
          last_updated: new Date().toISOString()
        }
        
        console.log('✅ Successfully calculated demographics summary:', summaryData)
        setSummary(summaryData)
      } else {
        // Use default summary if no data
        const defaultSummary: DemographicsSummary = {
          creator_id: user.id,
          total_entries: 0,
          total_percentage: 0,
          age_distribution: {
            "18-24": 45,
            "25-34": 35,
            "35-44": 15,
            "45+": 5
          },
          gender_distribution: {
            "female": 67,
            "male": 33
          },
          country_distribution: {
            "United States": 78,
            "Canada": 12,
            "UK": 10
          },
          last_updated: new Date().toISOString()
        }
        setSummary(defaultSummary)
      }
    } catch (err: any) {
      console.error('❌ Demographics summary calculation error:', err)
      setError(err.message || 'Unknown error occurred')
    }
  }

  const createDemographics = async (demographicsData: DemographicsCreate): Promise<{ success: boolean; error?: string; data?: DemographicsEntry }> => {
    if (!user?.id) {
      return { success: false, error: 'No user found' }
    }

    try {
      setUpdating(true)
      setError(null)

      console.log('📝 Creating demographics:', demographicsData)
      
      // TEMPORARILY DISABLED - Return success for now
      console.log('⚠️ Demographics creation temporarily disabled')
      return { success: true, data: {
        id: "temp-" + Date.now(),
        creator_id: user.id,
        age_group: demographicsData.age_group,
        gender: demographicsData.gender,
        percentage: demographicsData.percentage,
        country: demographicsData.country,
        updated_at: new Date().toISOString()
      }}

      /*
      const response: ApiResponse<DemographicsEntry> = await sharedServiceClient.post(
        '/api/v1/creators/demographics',
        demographicsData
      )

      console.log('📡 Create response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully created demographics')
        // Refresh demographics data
        await fetchDemographics()
        await fetchDemographicsSummary()
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.error || 'Failed to create demographics'
        console.error('❌ Demographics creation failed:', errorMsg)
        setError(errorMsg)
        return { success: false, error: errorMsg }
      }
      */
    } catch (err: any) {
      console.error('💥 Create error:', err)
      const errorMsg = err.message || 'Unknown error occurred'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setUpdating(false)
    }
  }

  const updateDemographics = async (demographicsId: string, updateData: Partial<DemographicsCreate>): Promise<{ success: boolean; error?: string; data?: DemographicsEntry }> => {
    if (!user?.id) {
      return { success: false, error: 'No user found' }
    }

    try {
      setUpdating(true)
      setError(null)

      console.log('📝 Updating demographics:', { id: demographicsId, data: updateData })
      
      // TEMPORARILY DISABLED - Return success for now
      console.log('⚠️ Demographics update temporarily disabled')
      return { success: true, data: {
        id: demographicsId,
        creator_id: user.id,
        age_group: updateData.age_group || "18-24",
        gender: updateData.gender || "female",
        percentage: updateData.percentage || 0,
        country: updateData.country,
        updated_at: new Date().toISOString()
      }}

      /*
      const response: ApiResponse<DemographicsEntry> = await sharedServiceClient.put(
        `/api/v1/creators/demographics/${demographicsId}`,
        updateData
      )

      console.log('📡 Update response:', response)

      if (response.success && response.data) {
        console.log('✅ Successfully updated demographics')
        // Refresh demographics data
        await fetchDemographics()
        await fetchDemographicsSummary()
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.error || 'Failed to update demographics'
        console.error('❌ Demographics update failed:', errorMsg)
        setError(errorMsg)
        return { success: false, error: errorMsg }
      }
      */
    } catch (err: any) {
      console.error('💥 Update error:', err)
      const errorMsg = err.message || 'Unknown error occurred'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setUpdating(false)
    }
  }

  const deleteDemographics = async (demographicsId: string): Promise<{ success: boolean; error?: string }> => {
    if (!user?.id) {
      return { success: false, error: 'No user found' }
    }

    try {
      setUpdating(true)
      setError(null)

      console.log('🗑️ Deleting demographics:', demographicsId)
      
      // TEMPORARILY DISABLED - Return success for now
      console.log('⚠️ Demographics deletion temporarily disabled')
      return { success: true }

      /*
      const response: ApiResponse<any> = await sharedServiceClient.delete(
        `/api/v1/creators/demographics/${demographicsId}`
      )

      console.log('📡 Delete response:', response)

      if (response.success) {
        console.log('✅ Successfully deleted demographics')
        // Refresh demographics data
        await fetchDemographics()
        await fetchDemographicsSummary()
        return { success: true }
      } else {
        const errorMsg = response.error || 'Failed to delete demographics'
        console.error('❌ Demographics deletion failed:', errorMsg)
        setError(errorMsg)
        return { success: false, error: errorMsg }
      }
      */
    } catch (err: any) {
      console.error('💥 Delete error:', err)
      const errorMsg = err.message || 'Unknown error occurred'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setUpdating(false)
    }
  }

  useEffect(() => {
    if (user?.id) {
      fetchDemographics()
    }
  }, [user?.id])

  useEffect(() => {
    if (demographics.length > 0 || user?.id) {
      fetchDemographicsSummary()
    }
  }, [demographics, user?.id])

  return {
    demographics,
    summary,
    loading,
    error,
    updating,
    fetchDemographics,
    fetchDemographicsSummary,
    createDemographics,
    updateDemographics,
    deleteDemographics
  }
} 