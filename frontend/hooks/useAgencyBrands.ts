import { useState, useEffect } from 'react'
import { campaignServiceClient } from '@/lib/api/client'

export interface AgencyBrand {
  id: string
  name: string
  logo: string
  status: 'active' | 'inactive' | 'pending'
  created_at: string
  updated_at: string
}

export function useAgencyBrands() {
  const [brands, setBrands] = useState<AgencyBrand[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAgencyBrands = async () => {
      try {
        setLoading(true)
        setError(null)
        
        console.log('🔍 [useAgencyBrands] Fetching agency brands...')
        
        const response = await campaignServiceClient.get('/api/v1/agency/brands')
        
        if (response.success && response.data) {
          console.log('✅ [useAgencyBrands] Brands received:', response.data)
          
          // Transform backend data to match component expectations
          const responseData = response.data as any
          const dataArray = Array.isArray(responseData) ? responseData : 
                           (responseData?.brands || responseData?.data || [])
          
          const transformedData = dataArray.map((brand: any) => ({
            id: brand.id || brand.brand_id,
            name: brand.name || brand.brand_name || 'Unknown Brand',
            logo: brand.logo || brand.brand_logo || brand.thumbnail_url || '/placeholder.svg?height=24&width=24',
            status: brand.status || 'active',
            created_at: brand.created_at || brand.createdAt || new Date().toISOString(),
            updated_at: brand.updated_at || brand.updatedAt || new Date().toISOString(),
          }))
          
          setBrands(transformedData)
        } else {
          console.error('❌ [useAgencyBrands] Failed to fetch brands:', response.error)
          setError(response.error || 'Failed to fetch agency brands')
          
          // Fallback to empty array if API fails
          setBrands([])
        }
      } catch (err: any) {
        console.error('❌ [useAgencyBrands] Error fetching brands:', err)
        setError(err.message || 'Failed to fetch agency brands')
        setBrands([])
      } finally {
        setLoading(false)
      }
    }

    fetchAgencyBrands()
  }, [])

  return {
    brands,
    loading,
    error,
  }
} 