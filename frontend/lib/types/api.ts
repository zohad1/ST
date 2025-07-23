// lib/types/api.ts - Essential API types for backend integration

export interface User {
  id: string
  email: string
  username: string
  role: 'creator' | 'agency' | 'brand' | 'admin'
  display_name?: string
  first_name?: string
  last_name?: string
  profile_image_url?: string
  email_verified: boolean
  is_active: boolean
  profile_completion_percentage: number
  userRole?: string // Legacy support
  created_at: string
  updated_at: string
}

export interface Campaign {
  id: string
  title: string
  description: string
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'
  creator_id?: string
  agency_id?: string
  brand_id?: string
  budget: number
  requirements: string[]
  deliverables: Deliverable[]
  start_date: string
  end_date: string
  created_at: string
  updated_at: string
}

export interface Deliverable {
  id: string
  campaign_id: string
  creator_id: string
  title: string
  description: string
  status: 'pending' | 'submitted' | 'approved' | 'rejected' | 'revision_requested'
  content_url?: string
  feedback?: string
  due_date: string
  submitted_at?: string
  reviewed_at?: string
  created_at: string
  updated_at: string
}

export interface Application {
  id: string
  campaign_id: string
  creator_id: string
  status: 'pending' | 'approved' | 'rejected'
  message?: string
  applied_at: string
  reviewed_at?: string
  campaign?: Campaign
  creator?: User
}

export interface Badge {
  id: string
  name: string
  description: string
  icon_url: string
  requirements: Record<string, any>
  reward_type: 'tier' | 'achievement' | 'milestone'
  tier_level?: number
  is_active: boolean
  created_at: string
}

export interface Analytics {
  total_campaigns: number
  active_campaigns: number
  completed_campaigns: number
  total_earnings: number
  pending_earnings: number
  total_deliverables: number
  approved_deliverables: number
  performance_score: number
}

export interface Payment {
  id: string
  user_id: string
  amount: number
  currency: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  payment_method: string
  transaction_id?: string
  created_at: string
  processed_at?: string
}

export interface Notification {
  id: string
  user_id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  action_url?: string
  created_at: string
  read_at?: string
}

export interface Integration {
  id: string
  user_id: string
  platform: 'tiktok' | 'instagram' | 'youtube' | 'discord' | 'stripe'
  status: 'connected' | 'disconnected' | 'error' | 'pending'
  account_info: Record<string, any>
  last_sync?: string
  created_at: string
  updated_at: string
}

// Response wrapper types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
  statusCode?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Query/Filter types
export interface CampaignFilters {
  status?: string[]
  budget_min?: number
  budget_max?: number
  niche?: string[]
  start_date?: string
  end_date?: string
  search?: string
}

export interface UserFilters {
  role?: string[]
  is_active?: boolean
  email_verified?: boolean
  search?: string
}
