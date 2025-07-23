"use client"

import { useState, useEffect } from 'react'
import { analyticsServiceClient } from '@/lib/api/client'

export interface Notification {
  id: string
  title: string
  message: string
  type: 'campaign' | 'payment' | 'system' | 'message'
  isRead: boolean
  createdAt: string
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true)
        setError(null)
        
        console.log('🔍 [useNotifications] Fetching notifications...')
        
        const response = await analyticsServiceClient.get('/api/v1/notifications')
        
        if (response.success && response.data) {
          console.log('✅ [useNotifications] Notifications received:', response.data)
          
          // Transform backend data to match component expectations
          const responseData = response.data as any
          const dataArray = Array.isArray(responseData) ? responseData : 
                           (responseData?.notifications || responseData?.data || [])
          
          const transformedData = dataArray.map((notification: any) => ({
            id: notification.id || notification.notification_id,
            title: notification.title || notification.subject || 'Notification',
            message: notification.message || notification.content || '',
            type: notification.type || 'system',
            isRead: notification.is_read || notification.read || false,
            createdAt: notification.created_at || notification.createdAt || new Date().toISOString(),
          }))
          
          setNotifications(transformedData)
        } else {
          console.error('❌ [useNotifications] Failed to fetch notifications:', response.error)
          setError(response.error || 'Failed to fetch notifications')
          setNotifications([])
        }
      } catch (err: any) {
        console.error('❌ [useNotifications] Error fetching notifications:', err)
        setError(err.message || 'Failed to fetch notifications')
        setNotifications([])
      } finally {
        setLoading(false)
      }
    }

    fetchNotifications()
  }, [])

  const unreadCount = notifications.filter(n => !n.isRead).length

  return {
    notifications,
    unreadCount,
    loading,
    error,
  }
}
