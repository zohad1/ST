"use client"

import { useState, useEffect, useCallback } from "react"
import { sharedServiceClient } from "@/lib/api/client"
import { API_CONFIG } from "@/lib/api/config"
import type { Notification } from "@/lib/types/api"

export function useNotifications(userId: string) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [unreadCount, setUnreadCount] = useState(0)

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await sharedServiceClient.get<Notification[]>(
        API_CONFIG.ENDPOINTS.SHARED.GET_NOTIFICATIONS.replace("{userId}", userId),
      )

      if (response.success && response.data) {
        setNotifications(response.data)
        setUnreadCount(response.data.filter((n) => !n.isRead).length)
      } else {
        throw new Error(response.message || "Failed to fetch notifications")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch notifications")
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    if (userId) {
      fetchNotifications()
    }
  }, [userId, fetchNotifications])

  const markAsRead = useCallback(async (notificationId: string) => {
    try {
      const response = await sharedServiceClient.post(
        API_CONFIG.ENDPOINTS.SHARED.MARK_NOTIFICATION_READ.replace("{id}", notificationId),
      )

      if (response.success) {
        setNotifications((prev) =>
          prev.map((notification) =>
            notification.id === notificationId ? { ...notification, isRead: true } : notification,
          ),
        )
        setUnreadCount((prev) => Math.max(0, prev - 1))
        return { success: true }
      }

      throw new Error(response.message || "Failed to mark as read")
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Failed to mark as read",
      }
    }
  }, [])

  const markAllAsRead = useCallback(async () => {
    try {
      const unreadNotifications = notifications.filter((n) => !n.isRead)

      await Promise.all(
        unreadNotifications.map((notification) =>
          sharedServiceClient.post(API_CONFIG.ENDPOINTS.SHARED.MARK_NOTIFICATION_READ.replace("{id}", notification.id)),
        ),
      )

      setNotifications((prev) => prev.map((notification) => ({ ...notification, isRead: true })))
      setUnreadCount(0)

      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Failed to mark all as read",
      }
    }
  }, [notifications])

  const sendNotification = useCallback(
    async (notificationData: {
      userId: string
      type: string
      title: string
      message: string
      actionUrl?: string
    }) => {
      try {
        const response = await sharedServiceClient.post<Notification>(
          API_CONFIG.ENDPOINTS.SHARED.SEND_NOTIFICATION,
          notificationData,
        )

        if (response.success && response.data) {
          if (notificationData.userId === userId) {
            setNotifications((prev) => [response.data!, ...prev])
            if (!response.data!.isRead) {
              setUnreadCount((prev) => prev + 1)
            }
          }
          return { success: true, data: response.data }
        }

        throw new Error(response.message || "Failed to send notification")
      } catch (err) {
        return {
          success: false,
          error: err instanceof Error ? err.message : "Failed to send notification",
        }
      }
    },
    [userId],
  )

  return {
    notifications,
    loading,
    error,
    unreadCount,
    markAsRead,
    markAllAsRead,
    sendNotification,
    refetch: fetchNotifications,
  }
}
