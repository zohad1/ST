"use client"

import { useState, useEffect, useCallback } from "react"
import { analyticsServiceClient } from "@/lib/api/client"
import { API_CONFIG } from "@/lib/api/config"
import type { DashboardAnalytics, CampaignAnalytics, CreatorPerformance } from "@/lib/types/api"

interface AnalyticsFilters {
  timeRange?: "7d" | "30d" | "90d" | "1y"
  campaignId?: string
  creatorId?: string
}

export function useDashboardAnalytics(filters: AnalyticsFilters = {}) {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await analyticsServiceClient.get<DashboardAnalytics>(
        API_CONFIG.ENDPOINTS.ANALYTICS.DASHBOARD,
        filters,
      )

      if (response.success && response.data) {
        setAnalytics(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch analytics")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch analytics")
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  return {
    analytics,
    loading,
    error,
    refetch: fetchAnalytics,
  }
}

export function useCampaignAnalytics(campaignId: string, filters: AnalyticsFilters = {}) {
  const [analytics, setAnalytics] = useState<CampaignAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await analyticsServiceClient.get<CampaignAnalytics>(
        API_CONFIG.ENDPOINTS.ANALYTICS.CAMPAIGN_ANALYTICS.replace("{id}", campaignId),
        filters,
      )

      if (response.success && response.data) {
        setAnalytics(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch campaign analytics")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch campaign analytics")
    } finally {
      setLoading(false)
    }
  }, [campaignId, filters])

  useEffect(() => {
    if (campaignId) {
      fetchAnalytics()
    }
  }, [campaignId, fetchAnalytics])

  return {
    analytics,
    loading,
    error,
    refetch: fetchAnalytics,
  }
}

export function useCreatorPerformance(filters: AnalyticsFilters = {}) {
  const [performance, setPerformance] = useState<CreatorPerformance[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPerformance = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await analyticsServiceClient.get<CreatorPerformance[]>(
        API_CONFIG.ENDPOINTS.ANALYTICS.CREATOR_PERFORMANCE,
        filters,
      )

      if (response.success && response.data) {
        setPerformance(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch creator performance")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch creator performance")
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchPerformance()
  }, [fetchPerformance])

  const exportReport = useCallback(
    async (format: "csv" | "pdf" = "csv") => {
      try {
        const response = await analyticsServiceClient.get(API_CONFIG.ENDPOINTS.ANALYTICS.EXPORT_REPORT, {
          ...filters,
          format,
        })

        if (response.success) {
          return { success: true, data: response.data }
        }

        throw new Error(response.message || "Export failed")
      } catch (err) {
        return {
          success: false,
          error: err instanceof Error ? err.message : "Export failed",
        }
      }
    },
    [filters],
  )

  return {
    performance,
    loading,
    error,
    exportReport,
    refetch: fetchPerformance,
  }
}
