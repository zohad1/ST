import { useState, useEffect } from "react"
import { userServiceClient } from "@/lib/api/client"
import { useAuth } from '@/context/authContext'
import { useToast } from "./use-toast"

export interface AgencySettings {
  // Agency Profile
  agencyName: string
  website?: string
  description?: string
  email: string
  phone?: string
  address?: string
  timezone: string
  logo?: string
  
  // Notification Preferences
  notifications: {
    campaignEmail: boolean
    campaignSMS: boolean
    campaignInApp: boolean
    financialEmail: boolean
    financialSMS: boolean
    financialInApp: boolean
    systemEmail: boolean
    systemSMS: boolean
    systemInApp: boolean
  }
  
  // Regional Settings
  currency: string
  dateFormat: string
  timeFormat: string
  weekStartsOn: string
  
  // Compliance
  gdprCompliance: boolean
  dataRetentionPeriod: string
  taxId?: string
  
  // Privacy
  profileVisibility: boolean
  
  // Notification Timing
  quietHoursStart: string
  quietHoursEnd: string
  digestFrequency: string
  weekendNotifications: boolean
}

export interface IntegrationStatus {
  name: string
  status: "connected" | "disconnected"
  lastSync: string
  icon: string
}

const defaultSettings: AgencySettings = {
  agencyName: "",
  website: "",
  description: "",
  email: "",
  phone: "",
  address: "",
  timezone: "est",
  logo: "",
  
  notifications: {
    campaignEmail: true,
    campaignSMS: false,
    campaignInApp: true,
    financialEmail: true,
    financialSMS: true,
    financialInApp: true,
    systemEmail: true,
    systemSMS: false,
    systemInApp: true,
  },
  
  currency: "usd",
  dateFormat: "mdy",
  timeFormat: "12",
  weekStartsOn: "sunday",
  
  gdprCompliance: true,
  dataRetentionPeriod: "90",
  taxId: "",
  
  profileVisibility: true,
  
  quietHoursStart: "22",
  quietHoursEnd: "8",
  digestFrequency: "weekly",
  weekendNotifications: false,
}

export function useAgencySettings() {
  const { user } = useAuth()
  const { toast } = useToast()
  
  const [settings, setSettings] = useState<AgencySettings>(defaultSettings)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([
    { name: "TikTok Shop", status: "disconnected", lastSync: "Setup recommended", icon: "🎵" },
    { name: "Twilio", status: "disconnected", lastSync: "Setup recommended", icon: "📱" },
    { name: "SendGrid", status: "disconnected", lastSync: "Setup recommended", icon: "📧" },
    { name: "Stripe", status: "disconnected", lastSync: "Setup recommended", icon: "💳" },
    { name: "Discord", status: "disconnected", lastSync: "Coming soon", icon: "💬" },
  ])

  // Load settings from backend
  const loadSettings = async () => {
    if (!user?.id) return

    try {
      setLoading(true)
      setError(null)

      console.log("🔧 Loading agency settings for user:", user.id)

      // Try to load settings from backend, but gracefully handle if endpoint doesn't exist
      try {
        const response = await userServiceClient.get<AgencySettings>("/api/v1/agency/settings")

        if (response.success && response.data) {
          console.log("✅ Settings loaded successfully:", response.data)
          setSettings({ ...defaultSettings, ...response.data })
          return
        }
      } catch (apiError: any) {
        console.log("📝 Agency settings endpoint not available, using defaults with user data")
      }

      // Use defaults with user data (either no response or API error)
      console.log("📝 Using defaults with user data")
      setSettings({
        ...defaultSettings,
        agencyName: user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : "Creator Circle Agency",
        email: user.email || "",
      })
      
    } catch (error: any) {
      console.error("❌ Failed to load settings:", error)
      setError(null) // Don't show error to user for missing endpoints
      
      // Use defaults with user data on error
      setSettings({
        ...defaultSettings,
        agencyName: user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : "Creator Circle Agency",
        email: user.email || "",
      })
    } finally {
      setLoading(false)
    }
  }

  // Save settings to backend
  const saveSettings = async (newSettings: Partial<AgencySettings>) => {
    if (!user?.id) {
      toast({
        title: "Error",
        description: "User not authenticated",
        variant: "destructive",
      })
      return { success: false, error: "User not authenticated" }
    }

    try {
      setSaving(true)
      setError(null)

      console.log("💾 Saving agency settings:", newSettings)

      // Try to save to backend, but gracefully handle if endpoint doesn't exist
      try {
        const response = await userServiceClient.put<AgencySettings>(
          "/api/v1/agency/settings",
          newSettings
        )

        if (response.success && response.data) {
          console.log("✅ Settings saved successfully")
          setSettings(response.data)
          
          toast({
            title: "Settings saved",
            description: "Your agency settings have been updated successfully.",
            duration: 3000,
          })
          
          return { success: true, data: response.data }
        }
      } catch (apiError: any) {
        console.log("📝 Settings save endpoint not available, updating locally")
      }

      // If backend save fails, update locally and show success
      console.log("💾 Updating settings locally")
      setSettings(prev => ({ ...prev, ...newSettings }))
      
      toast({
        title: "Settings updated",
        description: "Your settings have been updated locally. Backend integration coming soon.",
        duration: 3000,
      })
      
      return { success: true, data: { ...settings, ...newSettings } }
      
    } catch (error: any) {
      console.error("❌ Settings save error:", error)
      const errorMsg = "Settings updated locally"
      
      // Even on error, update locally for now
      setSettings(prev => ({ ...prev, ...newSettings }))
      
      toast({
        title: "Settings updated",
        description: "Your settings have been updated locally.",
        duration: 3000,
      })
      
      return { success: true, data: { ...settings, ...newSettings } }
    } finally {
      setSaving(false)
    }
  }

  // Update local settings (without saving)
  const updateSettings = (newSettings: Partial<AgencySettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }))
  }

  // Load integrations status
  const loadIntegrations = async () => {
    try {
      console.log("🔌 Loading integration status...")
      
      // Try to load from backend, but gracefully handle if endpoint doesn't exist
      try {
        const response = await userServiceClient.get<IntegrationStatus[]>("/api/v1/agency/integrations")
        
        if (response.success && response.data) {
          console.log("✅ Integrations loaded:", response.data)
          setIntegrations(response.data)
          return
        }
      } catch (apiError: any) {
        console.log("📝 Integrations endpoint not available, using defaults")
      }
      
      console.log("📝 Using default integration status")
      // Keep default disconnected status - already set in useState
      
    } catch (error: any) {
      console.log("📝 Using default integration status")
      // Keep default disconnected status - already set in useState
    }
  }

  // Load settings on mount
  useEffect(() => {
    if (user?.id) {
      loadSettings()
      loadIntegrations()
    }
  }, [user?.id])

  return {
    // Data
    settings,
    integrations,
    
    // States
    loading,
    saving,
    error,
    
    // Actions
    updateSettings,
    saveSettings,
    loadSettings,
    loadIntegrations,
  }
} 