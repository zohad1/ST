"use client"

import { useState, useEffect } from "react"
import { ChevronDown, Filter, Plus, Search, Users, RefreshCw, Calendar, DollarSign, TrendingUp, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { AgencySidebar } from "@/components/agency/navigation/agency-sidebar"
import { AgencyHeader } from "@/components/agency/navigation/agency-header"
import { CampaignCreationModal } from "@/components/agency/campaign-creation-modal"
import { CampaignActionsDropdown } from "@/components/agency/campaign-actions-dropdown"
import { CampaignDetailsModal } from "@/components/agency/campaign-details-modal"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/hooks/useAuth"

// Import the dashboard hooks for real data
import { 
  useCampaigns, 
  type Campaign as ApiCampaign,
  type DashboardAnalytics
} from "@/hooks/useDashboard"

// Import Auth Debug Component for development
import { AuthDebug } from "@/components/debug/AuthDebug"

type CampaignStatus = "draft" | "active" | "paused" | "completed" | "cancelled"
type CampaignProgress = "ahead" | "on-track" | "behind"

interface CampaignDisplay extends ApiCampaign {
  progress?: CampaignProgress
  gmv_formatted?: string
  daysOverdue?: number
}

export default function CampaignsPage() {
  const { user, isAuthenticated } = useAuth()
  const { toast } = useToast()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignDisplay | null>(null)
  const [showCampaignModal, setShowCampaignModal] = useState(false)
  const [showCampaignDetailsModal, setShowCampaignDetailsModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [refreshing, setRefreshing] = useState(false)

  // Helper functions - moved to top to avoid hoisting issues
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A"
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const calculateDaysOverdue = (endDate?: string) => {
    if (!endDate) return 0
    const end = new Date(endDate)
    const now = new Date()
    const diffTime = now.getTime() - end.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return Math.max(0, diffDays)
  }

  // Fetch campaigns data from backend
  const {
    campaigns: apiCampaigns,
    loading: campaignsLoading,
    error: campaignsError,
    refetch: refetchCampaigns,
  } = useCampaigns(statusFilter === "all" ? undefined : statusFilter)

  // Process campaigns data for display
  const campaigns: CampaignDisplay[] = (apiCampaigns || []).map(campaign => {
    const current = campaign.current_posts || 0
    const target = campaign.target_posts || 1
    const progress = (current / target) * 100
    
    let progressStatus: CampaignProgress = "on-track"
    if (progress > 110) progressStatus = "ahead"
    else if (progress < 80) progressStatus = "behind"

    return {
      ...campaign,
      progress: progressStatus,
      gmv_formatted: formatCurrency(campaign.current_gmv || 0),
      daysOverdue: campaign.status === "cancelled" ? calculateDaysOverdue(campaign.end_date) : undefined
    }
  })

  // Filter campaigns based on search term
  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Handle data refresh
  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refetchCampaigns()
      toast({
        title: "Data refreshed",
        description: "Campaign data has been updated successfully.",
      })
    } catch (error) {
      toast({
        title: "Refresh failed", 
        description: "Failed to refresh campaign data. Please try again.",
        variant: "destructive",
      })
    } finally {
      setRefreshing(false)
    }
  }

  // Handle errors
  useEffect(() => {
    if (campaignsError && !campaignsLoading) {
      toast({
        title: "Error loading campaigns",
        description: campaignsError,
        variant: "destructive",
      })
    }
  }, [campaignsError, campaignsLoading, toast])

  const getStatusColor = (status: CampaignStatus) => {
    switch (status) {
      case "active":
        return "bg-green-500"
      case "paused":
        return "bg-yellow-500"
      case "completed":
        return "bg-blue-500"
      case "cancelled":
        return "bg-red-500"
      case "draft":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  const getProgressColor = (progress?: CampaignProgress) => {
    switch (progress) {
      case "ahead":
        return "bg-green-500"
      case "on-track":
        return "bg-yellow-500"
      case "behind":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const handleCampaignClick = (campaign: CampaignDisplay) => {
    setSelectedCampaign(campaign)
    setShowCampaignDetailsModal(true)
  }

  const handleViewAnalytics = (campaignId: string) => {
    const campaign = campaigns.find(c => c.id === campaignId)
    if (campaign) {
      setSelectedCampaign(campaign)
      setShowCampaignDetailsModal(true)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <AgencySidebar isMobileOpen={isMobileSidebarOpen} onMobileClose={() => setIsMobileSidebarOpen(false)} />

      <div className="lg:ml-16 xl:ml-60 min-h-screen transition-all duration-300">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b border-gray-800">
          <Button variant="ghost" size="sm" onClick={() => setIsMobileSidebarOpen(true)}>
            <ChevronDown className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold">Campaigns</h1>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        <AgencyHeader />
        <main className="p-4 sm:p-6">
          {/* Auth Debug Component */}
          {process.env.NODE_ENV === 'development' && <AuthDebug />}

          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold">Campaigns</h1>
              <p className="text-gray-400">
                Manage and track your agency's campaigns
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                onClick={handleRefresh}
                disabled={refreshing}
                variant="outline"
                className="bg-gray-900 border-gray-800 hover:bg-gray-800"
              >
                {refreshing ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Refresh
              </Button>
              <Button 
                onClick={() => setShowCampaignModal(true)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Campaign
              </Button>
            </div>
          </div>

          {/* Summary Cards */}
          {!campaignsLoading && campaigns.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Total Campaigns</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{campaigns.length}</div>
                </CardContent>
              </Card>
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Active Campaigns</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaigns.filter(c => c.status === 'active').length}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Total GMV</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(campaigns.reduce((sum, c) => sum + (c.current_gmv || 0), 0))}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Total Creators</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaigns.reduce((sum, c) => sum + (c.current_creators || 0), 0)}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Filters and Search */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search campaigns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gray-900 border-gray-800 focus:border-purple-500"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="bg-gray-900 border-gray-800 hover:bg-gray-800">
                  <Filter className="h-4 w-4 mr-2" />
                  Status: {statusFilter === "all" ? "All" : statusFilter}
                  <ChevronDown className="h-4 w-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setStatusFilter("all")}>All</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("active")}>Active</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("paused")}>Paused</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("completed")}>Completed</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("draft")}>Draft</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Campaigns Table */}
          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-0">
              {campaignsLoading ? (
                <div className="p-6">
                  <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="flex items-center space-x-4">
                        <Skeleton className="h-12 w-12 rounded-full bg-gray-800" />
                        <div className="space-y-2 flex-1">
                          <Skeleton className="h-4 w-[250px] bg-gray-800" />
                          <Skeleton className="h-4 w-[200px] bg-gray-800" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : campaignsError ? (
                <div className="p-6 text-center">
                  <p className="text-red-400 mb-4">Error loading campaigns: {campaignsError}</p>
                  <Button onClick={handleRefresh} variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again
                  </Button>
                </div>
              ) : filteredCampaigns.length === 0 ? (
                <div className="p-6 text-center">
                  <p className="text-gray-400 mb-4">
                    {campaigns.length === 0 
                      ? "No campaigns found. Create your first campaign to get started."
                      : "No campaigns match your search criteria."
                    }
                  </p>
                  {campaigns.length === 0 && (
                    <Button onClick={() => setShowCampaignModal(true)} className="bg-purple-600 hover:bg-purple-700">
                      <Plus className="h-4 w-4 mr-2" />
                      Create First Campaign
                    </Button>
                  )}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-800">
                      <TableHead className="text-gray-400">Campaign</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">GMV</TableHead>
                      <TableHead className="text-gray-400">Creators</TableHead>
                      <TableHead className="text-gray-400">Progress</TableHead>
                      <TableHead className="text-gray-400">End Date</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCampaigns.map((campaign) => (
                      <TableRow
                        key={campaign.id}
                        className="border-gray-800 hover:bg-gray-800/50 cursor-pointer"
                        onClick={() => handleCampaignClick(campaign)}
                      >
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
                              <span className="text-purple-400 font-bold text-sm">
                                {campaign.name.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <div className="font-medium">{campaign.name}</div>
                              <div className="text-sm text-gray-400 truncate max-w-[200px]">
                                {campaign.description || "No description"}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant="outline" 
                            className={`${getStatusColor(campaign.status)} text-white border-0`}
                          >
                            {campaign.status}
                            {campaign.daysOverdue && (
                              <span className="ml-1">({campaign.daysOverdue}d overdue)</span>
                            )}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-bold">
                          {formatCurrency(campaign.current_gmv || 0)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-gray-400" />
                            <span>
                              {campaign.current_creators || 0}/{campaign.target_creators || 0}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <Progress
                              value={((campaign.current_posts || 0) / (campaign.target_posts || 1)) * 100}
                              className="h-2"
                              indicatorClassName={getProgressColor(campaign.progress)}
                            />
                            <div className="text-xs text-gray-400">
                              {campaign.current_posts || 0}/{campaign.target_posts || 0} posts
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {formatDate(campaign.end_date)}
                            {campaign.daysOverdue && (
                              <div className="text-red-400 text-xs">{campaign.daysOverdue} days overdue</div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <CampaignActionsDropdown
                            campaign={campaign}
                            onViewAnalytics={() => handleViewAnalytics(campaign.id)}
                            onEdit={() => handleCampaignClick(campaign)}
                            onToggleStatus={() => {
                              // Refresh campaigns after status update
                              handleRefresh()
                            }}
                            onMessageCreators={(campaignId) => {
                              // Navigate to messaging or open messaging modal
                              console.log("Message creators for campaign:", campaignId)
                              toast({
                                title: "Feature Coming Soon",
                                description: "Creator messaging will be available soon.",
                              })
                            }}
                            onDelete={() => {
                              // Refresh campaigns after deletion
                              handleRefresh()
                            }}
                            onRefresh={handleRefresh}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </main>
      </div>

      {/* Campaign Creation Modal */}
      <CampaignCreationModal 
        isOpen={showCampaignModal} 
        onClose={() => setShowCampaignModal(false)} 
      />

      {/* Campaign Details Modal - Simple implementation for now */}
      {selectedCampaign && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold">{selectedCampaign.name}</h2>
                  <p className="text-gray-400">{selectedCampaign.description || "No description"}</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => {
                    setSelectedCampaign(null)
                    setShowCampaignDetailsModal(false)
                  }}
                >
                  ✕
                </Button>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-400">Status</p>
                  <Badge className={`${getStatusColor(selectedCampaign.status)} text-white border-0`}>
                    {selectedCampaign.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Current GMV</p>
                  <p className="font-bold text-green-400">{formatCurrency(selectedCampaign.current_gmv || 0)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Creators</p>
                  <p className="font-medium">{selectedCampaign.current_creators || 0}/{selectedCampaign.target_creators || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Posts</p>
                  <p className="font-medium">{selectedCampaign.current_posts || 0}/{selectedCampaign.target_posts || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Start Date</p>
                  <p className="font-medium">{formatDate(selectedCampaign.start_date)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">End Date</p>
                  <p className="font-medium">{formatDate(selectedCampaign.end_date)}</p>
                </div>
              </div>

              <div className="mb-6">
                <p className="text-sm text-gray-400 mb-2">Post Progress</p>
                <Progress
                  value={((selectedCampaign.current_posts || 0) / (selectedCampaign.target_posts || 1)) * 100}
                  className="h-2 mb-2"
                  indicatorClassName={getProgressColor(selectedCampaign.progress)}
                />
                <p className="text-xs text-gray-400">
                  {Math.round(((selectedCampaign.current_posts || 0) / (selectedCampaign.target_posts || 1)) * 100)}% complete
                </p>
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={() => handleViewAnalytics(selectedCampaign.id)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Analytics
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    setSelectedCampaign(null)
                    setShowCampaignDetailsModal(false)
                  }}
                  className="border-gray-700 hover:bg-gray-800"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
