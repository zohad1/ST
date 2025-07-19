import { useState, useEffect, useMemo } from "react"
import { useToast } from "@/hooks/use-toast"
import { 
  useCampaignApplications, 
  useCampaigns, 
  useApplicationStats, 
  useReviewApplication,
  useBulkReviewApplications,
  type Application,
  type ApplicationFilters 
} from "@/hooks/useApplications"

// Date range type for filters
interface DateRange {
  from?: Date
  to?: Date
}

interface UseCreatorApplicationsReturn {
  // State
  searchQuery: string
  setSearchQuery: (query: string) => void
  statusFilter: string
  setStatusFilter: (status: string) => void
  campaignFilter: string
  setCampaignFilter: (campaign: string) => void
  selectedCampaignId: string
  setSelectedCampaignId: (id: string) => void
  dateRange: DateRange | undefined
  setDateRange: (range: DateRange | undefined) => void
  showFilters: boolean
  setShowFilters: (show: boolean) => void
  selectedApplications: string[]
  setSelectedApplications: (apps: string[]) => void
  selectedApplication: Application | null
  setSelectedApplication: (app: Application | null) => void
  showInviteModal: boolean
  setShowInviteModal: (show: boolean) => void
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  inviteEmails: string
  setInviteEmails: (emails: string) => void
  selectedCampaignForInvite: string
  setSelectedCampaignForInvite: (campaign: string) => void
  
  // Data
  campaigns: any[]
  applications: Application[]
  filteredApplications: Application[]
  stats: any
  
  // Loading states
  campaignsLoading: boolean
  applicationsLoading: boolean
  statsLoading: boolean
  applicationsError: any
  
  // Mutations
  reviewMutation: any
  bulkReviewMutation: any
  
  // Statistics
  totalApplications: number
  pendingApplications: number
  approvedApplications: number
  approvalRate: number
  
  // Actions
  handleSelectAll: () => void
  handleSelectApplication: (id: string) => void
  handleBulkApprove: () => Promise<void>
  handleBulkReject: () => Promise<void>
  handleApproveApplication: (id: string) => Promise<void>
  handleRejectApplication: (id: string) => Promise<void>
  handleSendInvites: () => void
  copyToClipboard: (text: string) => void
  refetchApplications: () => void
  
  // Utilities
  formatNumber: (num: number) => string
  formatCurrency: (amount: number) => string
  getStatusColor: (status: string) => string
  getStatusIcon: (status: string) => any
}

export function useCreatorApplications(): UseCreatorApplicationsReturn {
  const { toast } = useToast()
  
  // State management
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("All")
  const [campaignFilter, setCampaignFilter] = useState("All Campaigns")
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>("")
  const [dateRange, setDateRange] = useState<DateRange | undefined>()
  const [showFilters, setShowFilters] = useState(false)
  const [selectedApplications, setSelectedApplications] = useState<string[]>([])
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [inviteEmails, setInviteEmails] = useState("")
  const [selectedCampaignForInvite, setSelectedCampaignForInvite] = useState("")

  // Use the existing API hooks
  const { data: campaigns = [], isLoading: campaignsLoading } = useCampaigns()
  const { data: stats, isLoading: statsLoading } = useApplicationStats(selectedCampaignId)
  
  // Create filters object for the API
  const filters: ApplicationFilters = useMemo(() => ({
    status: statusFilter === "All" ? undefined : statusFilter,
    search: searchQuery,
    campaign_id: selectedCampaignId,
  }), [statusFilter, searchQuery, selectedCampaignId])
  
  // Get applications for the selected campaign
  const { 
    data: applications = [], 
    isLoading: applicationsLoading, 
    refetch: refetchApplications,
    error: applicationsError 
  } = useCampaignApplications(selectedCampaignId, filters)

  // Mutations
  const reviewMutation = useReviewApplication()
  const bulkReviewMutation = useBulkReviewApplications()

  // Set default campaign if available
  useEffect(() => {
    if (campaigns.length > 0 && !selectedCampaignId) {
      setSelectedCampaignId(campaigns[0].id)
    }
  }, [campaigns, selectedCampaignId])

  // Filter applications based on search query and other filters
  const filteredApplications = useMemo(() => {
    if (!applications) return []
    
    return applications.filter(application => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const creatorName = `${application.creator?.first_name || ''} ${application.creator?.last_name || ''}`.toLowerCase()
        const creatorEmail = application.creator?.email?.toLowerCase() || ''
        const campaignName = application.campaign?.name?.toLowerCase() || ''
        
        if (!creatorName.includes(query) && !creatorEmail.includes(query) && !campaignName.includes(query)) {
          return false
        }
      }
      
      // Status filter
      if (statusFilter !== "All" && application.status !== statusFilter) {
        return false
      }
      
      // Date range filter
      if (dateRange?.from && dateRange?.to) {
        const appliedDate = new Date(application.applied_at)
        if (appliedDate < dateRange.from || appliedDate > dateRange.to) {
          return false
        }
      }
      
      return true
    })
  }, [applications, searchQuery, statusFilter, dateRange])

  // Calculate statistics
  const totalApplications = filteredApplications.length
  const pendingApplications = filteredApplications.filter(app => app.status === 'pending').length
  const approvedApplications = filteredApplications.filter(app => app.status === 'approved').length
  const approvalRate = totalApplications > 0 ? Math.round((approvedApplications / totalApplications) * 100) : 0

  // Selection handlers
  const handleSelectAll = () => {
    if (selectedApplications.length === filteredApplications.length) {
      setSelectedApplications([])
    } else {
      setSelectedApplications(filteredApplications.map(app => app.id))
    }
  }

  const handleSelectApplication = (id: string) => {
    setSelectedApplications(prev => 
      prev.includes(id) 
        ? prev.filter(appId => appId !== id)
        : [...prev, id]
    )
  }

  // Review handlers
  const handleApproveApplication = async (id: string) => {
    try {
      await reviewMutation.mutateAsync({
        applicationId: id,
        reviewData: { status: 'approved' }
      })
      
      toast({
        title: "Application approved",
        description: "The creator application has been approved successfully.",
        duration: 3000,
      })
      
      // Remove from selection if it was selected
      setSelectedApplications(prev => prev.filter(appId => appId !== id))
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to approve application. Please try again.",
        variant: "destructive",
        duration: 5000,
      })
    }
  }

  const handleRejectApplication = async (id: string) => {
    try {
      await reviewMutation.mutateAsync({
        applicationId: id,
        reviewData: { 
          status: 'rejected',
          rejection_reason: 'Does not meet campaign requirements'
        }
      })
      
      toast({
        title: "Application rejected",
        description: "The creator application has been rejected.",
        duration: 3000,
      })
      
      // Remove from selection if it was selected
      setSelectedApplications(prev => prev.filter(appId => appId !== id))
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to reject application. Please try again.",
        variant: "destructive",
        duration: 5000,
      })
    }
  }

  // Bulk actions
  const handleBulkApprove = async () => {
    if (selectedApplications.length === 0) return
    
    try {
      await bulkReviewMutation.mutateAsync({
        applicationIds: selectedApplications,
        action: 'approved'
      })
      
      toast({
        title: "Applications approved",
        description: `${selectedApplications.length} applications have been approved.`,
        duration: 3000,
      })
      
      setSelectedApplications([])
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to approve applications. Please try again.",
        variant: "destructive",
        duration: 5000,
      })
    }
  }

  const handleBulkReject = async () => {
    if (selectedApplications.length === 0) return
    
    try {
      await bulkReviewMutation.mutateAsync({
        applicationIds: selectedApplications,
        action: 'rejected',
        notes: 'Bulk rejection - does not meet campaign requirements'
      })
      
      toast({
        title: "Applications rejected",
        description: `${selectedApplications.length} applications have been rejected.`,
        duration: 3000,
      })
      
      setSelectedApplications([])
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to reject applications. Please try again.",
        variant: "destructive",
        duration: 5000,
      })
    }
  }

  // Utility functions
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case "approved":
        return "bg-green-800 text-green-400"
      case "rejected":
        return "bg-red-800 text-red-400"
      case "pending":
        return "bg-yellow-800 text-yellow-400"
      default:
        return "bg-gray-700 text-gray-400"
    }
  }

  const getStatusIcon = (status: string) => {
    // Return icon component classes/names that can be used with lucide-react
    switch (status) {
      case "approved":
        return "Check"
      case "rejected":
        return "X"
      case "pending":
        return "Clock"
      default:
        return "AlertCircle"
    }
  }

  // Other handlers
  const handleSendInvites = () => {
    // TODO: Implement invite functionality
    toast({
      title: "Feature Coming Soon",
      description: "Creator invitation feature will be available soon.",
    })
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: "Copied to clipboard",
        description: "The text has been copied to your clipboard.",
        duration: 2000,
      })
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Could not copy to clipboard. Please copy manually.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  return {
    // State
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    campaignFilter,
    setCampaignFilter,
    selectedCampaignId,
    setSelectedCampaignId,
    dateRange,
    setDateRange,
    showFilters,
    setShowFilters,
    selectedApplications,
    setSelectedApplications,
    selectedApplication,
    setSelectedApplication,
    showInviteModal,
    setShowInviteModal,
    sidebarOpen,
    setSidebarOpen,
    inviteEmails,
    setInviteEmails,
    selectedCampaignForInvite,
    setSelectedCampaignForInvite,
    
    // Data
    campaigns,
    applications,
    filteredApplications,
    stats,
    
    // Loading states
    campaignsLoading,
    applicationsLoading,
    statsLoading,
    applicationsError,
    
    // Mutations
    reviewMutation,
    bulkReviewMutation,
    
    // Statistics
    totalApplications,
    pendingApplications,
    approvedApplications,
    approvalRate,
    
    // Actions
    handleSelectAll,
    handleSelectApplication,
    handleBulkApprove,
    handleBulkReject,
    handleApproveApplication,
    handleRejectApplication,
    handleSendInvites,
    copyToClipboard,
    refetchApplications,
    
    // Utilities
    formatNumber,
    formatCurrency,
    getStatusColor,
    getStatusIcon,
  }
} 