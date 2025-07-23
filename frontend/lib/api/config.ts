// lib/api/config.ts - Updated configuration for microservices

// Type declaration for process.env in browser environment
declare const process: {
  env: {
    NODE_ENV: string;
    NEXT_PUBLIC_USER_SERVICE_URL?: string;
    NEXT_PUBLIC_CAMPAIGN_SERVICE_URL?: string;
    NEXT_PUBLIC_ANALYTICS_SERVICE_URL?: string;
    NEXT_PUBLIC_PAYMENT_SERVICE_URL?: string;
    NEXT_PUBLIC_INTEGRATION_SERVICE_URL?: string;
    NEXT_PUBLIC_SHARED_SERVICE_URL?: string;
  };
};

export const API_CONFIG = {
  // Service Base URLs
  SERVICES: {
    USER_SERVICE: process.env.NEXT_PUBLIC_USER_SERVICE_URL || "http://localhost:8000",
    CAMPAIGN_SERVICE: process.env.NEXT_PUBLIC_CAMPAIGN_SERVICE_URL || "http://localhost:8002", 
    ANALYTICS_SERVICE: process.env.NEXT_PUBLIC_ANALYTICS_SERVICE_URL || "http://localhost:8003",
    PAYMENT_SERVICE: process.env.NEXT_PUBLIC_PAYMENT_SERVICE_URL || "http://localhost:8004",
    INTEGRATION_SERVICE: process.env.NEXT_PUBLIC_INTEGRATION_SERVICE_URL || "http://localhost:8005",
    SHARED_SERVICE: process.env.NEXT_PUBLIC_SHARED_SERVICE_URL || "http://localhost:8006",
  },

  // API Endpoints organized by service
  ENDPOINTS: {
    // User Service (Authentication, Profile Management)
    AUTH: {
      LOGIN: "/api/v1/auth/login",
      REGISTER: "/api/v1/auth/signup",
      LOGOUT: "/api/v1/auth/logout",
      PROFILE: "/api/v1/auth/profile",
      VERIFY_EMAIL: "/api/v1/auth/verify-email",
      RESEND_VERIFICATION: "/api/v1/auth/resend-verification",
      REFRESH_TOKEN: "/api/v1/auth/refresh",
      FORGOT_PASSWORD: "/api/v1/auth/forgot-password",
      RESET_PASSWORD: "/api/v1/auth/reset-password",
    },

    USERS: {
      GET_PROFILE: "/api/v1/users/profile",
      UPDATE_PROFILE: "/api/v1/users/profile",
      GET_ALL: "/api/v1/users",
      GET_BY_ID: (id: string) => `/api/v1/users/${id}`,
      UPDATE_BY_ID: (id: string) => `/api/v1/users/${id}`,
      DELETE_BY_ID: (id: string) => `/api/v1/users/${id}`,
      SEARCH: "/api/v1/users/search",
    },

    // Badge System (Shared Service)
    BADGES: {
      GET_ALL: "/api/v1/badges",
      GET_STATS: "/api/v1/badges/stats",
      GET_LEADERBOARD: "/api/v1/badges/leaderboard",
      
      // Creator badges
      GET_CREATOR_BADGES: (creatorId: string) => `/api/v1/badges/creator/${creatorId}`,
      GET_CREATOR_PROGRESS: (creatorId: string) => `/api/v1/badges/creator/${creatorId}/progress`,
      GET_CREATOR_HISTORY: (creatorId: string) => `/api/v1/badges/creator/${creatorId}/history`,
      GET_CREATOR_SHOWCASE: (creatorId: string) => `/api/v1/badges/creator/${creatorId}/showcase`,
      GET_CREATOR_PACE: (creatorId: string) => `/api/v1/badges/creator/${creatorId}/pace`,
      GET_CREATOR_PACE_BY_TYPE: (creatorId: string, badgeType: string) => `/api/v1/badges/creator/${creatorId}/pace/${badgeType}`,
      
      // Current user badges (convenience endpoints)
      GET_MY_BADGES: "/api/v1/creators/badges",
      GET_MY_PROGRESS: "/api/v1/creators/badges/progress",
      GET_MY_HISTORY: "/api/v1/creators/badges/history",
      GET_MY_SHOWCASE: "/api/v1/creators/badges/showcase",
      
      // Admin functions
      CALCULATE_BADGES: (creatorId: string) => `/api/v1/badges/calculate/${creatorId}`,
    },

    // Campaign Service (Campaigns, Applications, Deliverables)
    CAMPAIGNS: {
      GET_ALL: "/api/v1/campaigns",
      CREATE: "/api/v1/campaigns",
      GET_BY_ID: (id: string) => `/api/v1/campaigns/${id}`,
      UPDATE: (id: string) => `/api/v1/campaigns/${id}`,
      DELETE: (id: string) => `/api/v1/campaigns/${id}`,
      
      // Campaign segments
      SEGMENTS: {
        GET: (campaignId: string) => `/api/v1/campaigns/${campaignId}/segments`,
        CREATE: (campaignId: string) => `/api/v1/campaigns/${campaignId}/segments`,
        UPDATE: (campaignId: string, segmentId: string) => `/api/v1/campaigns/${campaignId}/segments/${segmentId}`,
        DELETE: (campaignId: string, segmentId: string) => `/api/v1/campaigns/${campaignId}/segments/${segmentId}`,
      },

      // Bonus tiers
      BONUS_TIERS: {
        GET: (campaignId: string) => `/api/v1/campaigns/${campaignId}/bonus-tiers`,
        CREATE: (campaignId: string) => `/api/v1/campaigns/${campaignId}/bonus-tiers`,
        UPDATE: (campaignId: string, tierId: string) => `/api/v1/campaigns/${campaignId}/bonus-tiers/${tierId}`,
        DELETE: (campaignId: string, tierId: string) => `/api/v1/campaigns/${campaignId}/bonus-tiers/${tierId}`,
      },

      // Leaderboard bonuses
      LEADERBOARD: {
        GET: (campaignId: string) => `/api/v1/campaigns/${campaignId}/leaderboard`,
        CREATE: (campaignId: string) => `/api/v1/campaigns/${campaignId}/leaderboard`,
        UPDATE: (campaignId: string, bonusId: string) => `/api/v1/campaigns/${campaignId}/leaderboard/${bonusId}`,
        DELETE: (campaignId: string, bonusId: string) => `/api/v1/campaigns/${campaignId}/leaderboard/${bonusId}`,
      },
    },

    // Applications
    APPLICATIONS: {
      GET_ALL: "/api/v1/applications",
      CREATE: "/api/v1/applications",
      GET_MY_APPLICATIONS: "/api/v1/applications/my-applications",
      REVIEW: (id: string) => `/api/v1/applications/${id}/review`,
      GET_BY_CAMPAIGN: (campaignId: string) => `/api/v1/applications/campaign/${campaignId}`,
    },

    // Deliverables
    DELIVERABLES: {
      GET_ALL: "/api/v1/deliverables",
      CREATE: "/api/v1/deliverables",
      GET_MY_DELIVERABLES: "/api/v1/deliverables/my-deliverables",
      REVIEW: (id: string) => `/api/v1/deliverables/${id}/review`,
      GET_BY_CAMPAIGN: (campaignId: string) => `/api/v1/deliverables/campaign/${campaignId}`,
      GET_BY_CAMPAIGN_CREATOR: (campaignId: string) => `/api/v1/deliverables/campaign/${campaignId}/creator`,
    },

    // Dashboard (Campaign Service)
    DASHBOARD: {
      ANALYTICS: "/api/v1/dashboard/analytics",
      CAMPAIGNS: "/api/v1/dashboard/campaigns",
      CREATE_CAMPAIGN: "/api/v1/dashboard/campaigns",
      GET_CAMPAIGN: (id: string) => `/api/v1/dashboard/campaigns/${id}`,
      UPDATE_CAMPAIGN: (id: string) => `/api/v1/dashboard/campaigns/${id}`,
      
      APPLICATIONS: "/api/v1/dashboard/applications",
      APPLY_TO_CAMPAIGN: (campaignId: string) => `/api/v1/dashboard/campaigns/${campaignId}/apply`,
      REVIEW_APPLICATION: (applicationId: string) => `/api/v1/dashboard/applications/${applicationId}/review`,
      
      DELIVERABLES: "/api/v1/dashboard/deliverables",
      SUBMIT_CONTENT: (deliverableId: string) => `/api/v1/dashboard/deliverables/${deliverableId}/submit`,
      REVIEW_CONTENT: (deliverableId: string) => `/api/v1/dashboard/deliverables/${deliverableId}/review`,
      
      CREATOR_PERFORMANCE: "/api/v1/dashboard/creator-performance",
      LEADERBOARD: "/api/v1/dashboard/leaderboard",
    },

    // Analytics Service 
    ANALYTICS: {
      DASHBOARD: "/api/v1/analytics/dashboard",
      CAMPAIGN: (id: string) => `/api/v1/analytics/campaigns/${id}`,
      CREATOR: (id: string) => `/api/v1/analytics/creators/${id}`,
      GMV: "/api/v1/analytics/gmv",
      REAL_TIME: "/api/v1/analytics/real-time",
      TRENDS: "/api/v1/analytics/trends",
      PERFORMANCE: "/api/v1/analytics/performance",
    },

    // Payment Service
    PAYMENTS: {
      OVERVIEW: "/api/v1/payments/overview",
      HISTORY: "/api/v1/payments/history",
      PROCESS: "/api/v1/payments/process",
      METHODS: "/api/v1/payments/methods",
      PAYOUTS: "/api/v1/payments/payouts",
    },

    // Earnings Service (separate from payments)
    EARNINGS: {
      GET_ALL: "/api/v1/earnings",
      GET_CREATOR: (creatorId: string) => `/api/v1/earnings/creator/${creatorId}`,
      GET_CREATOR_SUMMARY: (creatorId: string) => `/api/v1/earnings/creator/${creatorId}/summary`,
      GET_CAMPAIGN_TOTALS: (campaignId: string) => `/api/v1/earnings/campaign/${campaignId}/totals`,
      CALCULATE: "/api/v1/earnings/calculate",
      PROCESS_DELIVERABLE: "/api/v1/earnings/process-deliverable",
      PROCESS_GMV: "/api/v1/earnings/process-gmv",
    },

    // Integration Service
    INTEGRATIONS: {
      GET_ALL: "/api/v1/integrations",
      CONNECT: (id: string) => `/api/v1/integrations/${id}/connect`,
      DISCONNECT: (id: string) => `/api/v1/integrations/${id}/disconnect`,
      GET_STATUS: (id: string) => `/api/v1/integrations/${id}/status`,
      SYNC_DATA: (id: string) => `/api/v1/integrations/${id}/sync`,
      
      // TikTok Shop
      TIKTOK_SHOP: {
        AUTHORIZE: "/api/v1/integrations/tiktok-shop/authorize",
        SYNC_SALES: "/api/v1/integrations/tiktok-shop/sync-sales",
        GET_PRODUCTS: "/api/v1/integrations/tiktok-shop/products",
      },

      // TikTok Video Integration
      TIKTOK_VIDEO: {
        SYNC_VIDEOS: "/api/v1/integrations/tiktok/sync-videos",
        MARK_DELIVERABLE: "/api/v1/integrations/tiktok/mark-deliverable",
        ATTRIBUTE_GMV: "/api/v1/integrations/tiktok/attribute-gmv",
      },

      // Discord
      DISCORD: {
        AUTHORIZE: "/api/v1/integrations/discord/authorize",
        ASSIGN_ROLES: "/api/v1/integrations/discord/assign-roles",
        CREATE_CHANNELS: "/api/v1/integrations/discord/create-channels",
      },

      // SMS (SendBlue)
      SMS: {
        SEND_BULK: "/api/v1/integrations/sms/send-bulk",
        SEND_INDIVIDUAL: "/api/v1/integrations/sms/send-individual",
        GET_HISTORY: "/api/v1/integrations/sms/history",
      },
    },

    // Shared Service (File uploads, notifications, etc.)
    SHARED: {
      UPLOAD_FILE: "/api/v1/shared/upload",
      DELETE_FILE: (id: string) => `/api/v1/shared/files/${id}`,
      GET_FILE: (id: string) => `/api/v1/shared/files/${id}`,
    },

    // Notifications
    NOTIFICATIONS: {
      GET_ALL: "/api/v1/notifications",
      MARK_READ: (id: string) => `/api/v1/notifications/${id}/read`,
      MARK_ALL_READ: "/api/v1/notifications/read-all",
      DELETE: (id: string) => `/api/v1/notifications/${id}`,
      GET_SETTINGS: "/api/v1/notifications/settings",
      UPDATE_SETTINGS: "/api/v1/notifications/settings",
    },
  },

  // Request configuration
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second

  // Rate limiting
  RATE_LIMIT: {
    MAX_REQUESTS: 100,
    WINDOW_MS: 60000, // 1 minute
  },

  // Development settings
  ENABLE_DEVTOOLS: process.env.NODE_ENV === "development",
}

export const ENDPOINTS = API_CONFIG.ENDPOINTS

// Environment detection
export const isDevelopment = process.env.NODE_ENV === "development"
export const isProduction = process.env.NODE_ENV === "production"

// Default headers
export const DEFAULT_HEADERS = {
  "Content-Type": "application/json",
  "Accept": "application/json",
}

// Auth header helper
export const getAuthHeader = () => {
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// API error type for hooks
export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

// Additional helper functions for backward compatibility
export const getAuthHeaders = (token?: string | null) => {
  const authToken = token || (typeof window !== "undefined" ? localStorage.getItem("auth_token") : null)
  return authToken ? { Authorization: `Bearer ${authToken}` } : {}
}

export const REQUEST_TIMEOUT = API_CONFIG.TIMEOUT
