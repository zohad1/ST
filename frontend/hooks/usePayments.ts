"use client"

import { useState, useEffect, useCallback } from "react"
import { paymentServiceClient } from "@/lib/api/client"
import { API_CONFIG } from "@/lib/api/config"
import type { Earnings, PaymentRecord, PaymentMethod } from "@/lib/types/api"

export function useEarnings(userId: string) {
  const [earnings, setEarnings] = useState<Earnings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEarnings = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await paymentServiceClient.get<Earnings>(
        API_CONFIG.ENDPOINTS.PAYMENTS.GET_EARNINGS.replace("{userId}", userId),
      )

      if (response.success && response.data) {
        setEarnings(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch earnings")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch earnings")
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    if (userId) {
      fetchEarnings()
    }
  }, [userId, fetchEarnings])

  return {
    earnings,
    loading,
    error,
    refetch: fetchEarnings,
  }
}

export function usePaymentHistory(userId: string, filters: Record<string, any> = {}) {
  const [payments, setPayments] = useState<PaymentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPayments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await paymentServiceClient.get<PaymentRecord[]>(
        API_CONFIG.ENDPOINTS.PAYMENTS.GET_PAYMENT_HISTORY.replace("{userId}", userId),
        filters,
      )

      if (response.success && response.data) {
        setPayments(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch payment history")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch payment history")
    } finally {
      setLoading(false)
    }
  }, [userId, filters])

  useEffect(() => {
    if (userId) {
      fetchPayments()
    }
  }, [userId, fetchPayments])

  return {
    payments,
    loading,
    error,
    refetch: fetchPayments,
  }
}

export function usePaymentMethods(userId: string) {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPaymentMethods = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await paymentServiceClient.get<PaymentMethod[]>(
        API_CONFIG.ENDPOINTS.PAYMENTS.GET_PAYMENT_METHODS.replace("{userId}", userId),
      )

      if (response.success && response.data) {
        setPaymentMethods(response.data)
      } else {
        throw new Error(response.message || "Failed to fetch payment methods")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch payment methods")
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    if (userId) {
      fetchPaymentMethods()
    }
  }, [userId, fetchPaymentMethods])

  const addPaymentMethod = useCallback(
    async (methodData: Partial<PaymentMethod>) => {
      try {
        const response = await paymentServiceClient.post<PaymentMethod>(
          API_CONFIG.ENDPOINTS.PAYMENTS.ADD_PAYMENT_METHOD,
          { ...methodData, userId },
        )

        if (response.success && response.data) {
          setPaymentMethods((prev) => [...prev, response.data!])
          return { success: true, data: response.data }
        }

        throw new Error(response.message || "Failed to add payment method")
      } catch (err) {
        return {
          success: false,
          error: err instanceof Error ? err.message : "Failed to add payment method",
        }
      }
    },
    [userId],
  )

  const updatePaymentMethod = useCallback(async (methodId: string, updates: Partial<PaymentMethod>) => {
    try {
      const response = await paymentServiceClient.put<PaymentMethod>(
        API_CONFIG.ENDPOINTS.PAYMENTS.UPDATE_PAYMENT_METHOD.replace("{id}", methodId),
        updates,
      )

      if (response.success && response.data) {
        setPaymentMethods((prev) => prev.map((method) => (method.id === methodId ? response.data! : method)))
        return { success: true, data: response.data }
      }

      throw new Error(response.message || "Failed to update payment method")
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Failed to update payment method",
      }
    }
  }, [])

  const deletePaymentMethod = useCallback(async (methodId: string) => {
    try {
      const response = await paymentServiceClient.delete(
        API_CONFIG.ENDPOINTS.PAYMENTS.DELETE_PAYMENT_METHOD.replace("{id}", methodId),
      )

      if (response.success) {
        setPaymentMethods((prev) => prev.filter((method) => method.id !== methodId))
        return { success: true }
      }

      throw new Error(response.message || "Failed to delete payment method")
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Failed to delete payment method",
      }
    }
  }, [])

  return {
    paymentMethods,
    loading,
    error,
    addPaymentMethod,
    updatePaymentMethod,
    deletePaymentMethod,
    refetch: fetchPaymentMethods,
  }
}
