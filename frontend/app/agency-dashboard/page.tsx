// app/agency-dashboard/page.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import {
  ArrowUpRight,
  ChevronDown,
  CircleDollarSign,
  Eye,
  Heart,
  Menu,
  MoreHorizontal,
  Plus,
  UserPlus,
  RefreshCw,
  TrendingUp,
  Users,
  Target,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { AgencySidebar } from "@/components/agency/navigation/agency-sidebar"
import { AgencyHeader } from "@/components/agency/navigation/agency-header"
import { RevenueGrowthChart } from "@/components/charts/revenue-growth-chart"
import { PostsPerDayChart } from "@/components/charts/posts-per-day-chart"
import { EngagementChart } from "@/components/charts/engagement-chart"
import { CampaignCreationModal } from "@/components/agency/campaign-creation-modal"
import { CampaignDetailsModal } from "@/components/agency/campaign-details-modal"

// Import hooks to fetch real data
import { 
  useDashboardAnalytics, 
  useCampaigns, 
  useCreatorPerformance,
  useDeliverables,
  type DashboardAnalytics,
  type Campaign,
  type CreatorPerformance,
  type Deliverable
} from "@/hooks/useDashboard"

// Import Auth Debug Component
import { AuthDebug } from "@/components/debug/AuthDebug"

// Import auth hook
import { useAuth } from "@/hooks/useAuth"

interface CampaignProgress {
  id: string
  name: string
  current_posts: number
  target_posts: number
  status: "ahead" | "on-track" | "behind"
  progress_percentage: number
}

export default function AgencyDashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated, refreshUser } = useAuth()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null)
  const [timeframe, setTimeframe] = useState("last_30_days")
  const [refreshing, setRefreshing] = useState(false)
  const [showCampaignModal, setShowCampaignModal] = useState(false)
  const [showCampaignDetailsModal, setShowCampaignDetailsModal] = useState(false)

  const { toast } = useToast()

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated) {
        console.log("🔒 Not authenticated, refreshing auth...")
        await refreshUser()
      }
    }
    checkAuth()
  }, [isAuthenticated, refreshUser])

  // Fetch real data from backend
  const {
    data: analytics,
    loading: analyticsLoading,
    error: analyticsError,
    refetch: refetchAnalytics,
  } = useDashboardAnalytics(timeframe)

  const {
    campaigns,
    loading: campaignsLoading,
    error: campaignsError,
    refetch: refetchCampaigns,
  } = useCampaigns("active") // Only show active campaigns

  const {
    performance: creatorPerformance,
    loading: performanceLoading,
    error: performanceError,
    refetch: refetchPerformance,
  } = useCreatorPerformance(undefined, timeframe, 10)

  // Note: Deliverables are fetched in the CampaignDetailsModal when a campaign is selected

  // SAFE DATA HANDLING: Ensure all data is properly typed and has fallbacks
  const safeCampaigns = Array.isArray(campaigns) ? campaigns : []
  const safeCreatorPerformance = Array.isArray(creatorPerformance) ? creatorPerformance : []
  const safeAnalytics = analytics && analytics.kpis ? analytics : null

  // Helper function to safely get KPI values
  const getKpiValue = (kpiPath: string): number => {
    if (!safeAnalytics) return 0
    const keys = kpiPath.split('.')
    let value: any = safeAnalytics
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key]
      } else {
        return 0
      }
    }
    return typeof value === 'number' ? value : 0
  }

  const getKpiGrowth = (kpiPath: string): number => {
    if (!safeAnalytics) return 0
    const keys = kpiPath.split('.')
    let value: any = safeAnalytics
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key]
      } else {
        return 0
      }
    }
    return typeof value === 'number' ? value : 0
  }

  // Handle data refresh
  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      // Refresh auth first
      await refreshUser()
      
      // Then refresh data
      await Promise.all([
        refetchAnalytics(),
        refetchCampaigns(),
        refetchPerformance(),
      ])
      toast({
        title: "Data refreshed",
        description: "Dashboard data has been updated successfully.",
      })
    } catch (error) {
      toast({
        title: "Refresh failed",
        description: "Failed to refresh dashboard data. Please try again.",
        variant: "destructive",
      })
    } finally {
      setRefreshing(false)
    }
  }

  const handleViewCampaignDetails = (campaign: Campaign) => {
    setSelectedCampaign(campaign)
    setShowCampaignDetailsModal(true)
  }

  // Handle errors - but don't show toast if loading
  useEffect(() => {
    if (!analyticsLoading && !campaignsLoading && !performanceLoading) {
      if (analyticsError || campaignsError || performanceError) {
        console.error('Dashboard errors:', { analyticsError, campaignsError, performanceError })
        // Don't show error toast on initial load as it might be auth-related
      }
    }
  }, [analyticsError, campaignsError, performanceError, analyticsLoading, campaignsLoading, performanceLoading])

  // Calculate campaign progress from real data - WITH SAFE ARRAY HANDLING
  const calculateCampaignProgress = (campaignsList: Campaign[]): CampaignProgress[] => {
    if (!Array.isArray(campaignsList)) {
      console.warn('calculateCampaignProgress received non-array:', campaignsList)
      return []
    }

    return campaignsList.map(campaign => {
      const current = campaign.current_posts || 0
      const target = campaign.target_posts || 1
      const progress = (current / target) * 100
      
      let status: "ahead" | "on-track" | "behind" = "on-track"
      if (progress > 110) status = "ahead"
      else if (progress < 80) status = "behind"

      return {
        id: campaign.id,
        name: campaign.name,
        current_posts: current,
        target_posts: target,
        status,
        progress_percentage: Math.min(progress, 100),
      }
    })
  }

  // SAFE: Use slice with safe array
  const campaignProgress = calculateCampaignProgress(safeCampaigns.slice(0, 4))

  const getStatusColor = (status: CampaignProgress["status"]) => {
    switch (status) {
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

  const getStatusText = (status: CampaignProgress["status"]) => {
    switch (status) {
      case "ahead":
        return "AHEAD"
      case "on-track":
        return "ON-TRACK"
      case "behind":
        return "BEHIND"
      default:
        return "UNKNOWN"
    }
  }

  const getStatusTextColor = (status: CampaignProgress["status"]) => {
    switch (status) {
      case "ahead":
        return "text-green-400"
      case "on-track":
        return "text-yellow-400"
      case "behind":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <AgencySidebar isMobileOpen={isMobileSidebarOpen} onMobileClose={() => setIsMobileSidebarOpen(false)} />

      <div className="lg:ml-16 xl:ml-60 min-h-screen transition-all duration-300">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b border-gray-800">
          <Button variant="ghost" size="sm" onClick={() => setIsMobileSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="font-semibold">Agency Dashboard</h1>
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
          
          {/* Header & Filters */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold">Agency Dashboard</h1>
              <p className="text-gray-400">
                Welcome back{user?.first_name ? `, ${user.first_name}` : ''}, here's your agency's performance overview
              </p>
            </div>
            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="bg-gray-900 border-gray-800 hover:bg-gray-800">
                    {timeframe.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} <ChevronDown className="h-4 w-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56">
                  <DropdownMenuCheckboxItem 
                    checked={timeframe === "last_7_days"}
                    onCheckedChange={() => setTimeframe("last_7_days")}
                  >
                    Last 7 days
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem 
                    checked={timeframe === "last_30_days"}
                    onCheckedChange={() => setTimeframe("last_30_days")}
                  >
                    Last 30 days
                  </DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem 
                    checked={timeframe === "last_90_days"}
                    onCheckedChange={() => setTimeframe("last_90_days")}
                  >
                    Last 90 days
                  </DropdownMenuCheckboxItem>
                </DropdownMenuContent>
              </DropdownMenu>
              
              <Button 
                onClick={handleRefresh}
                disabled={refreshing}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {refreshing ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                Refresh
              </Button>
            </div>
          </div>

          {/* KPI Cards - SAFE DATA ACCESS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {/* Total Views */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Total Views</CardTitle>
                <Eye className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                {analyticsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-20 bg-gray-800" />
                    <Skeleton className="h-4 w-24 bg-gray-800" />
                  </div>
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatNumber(getKpiValue('kpis.total_views.value'))}
                    </div>
                    <p className={`text-xs flex items-center ${
                      getKpiGrowth('kpis.total_views.growth') >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      <ArrowUpRight className="h-3 w-3 mr-1" />
                      {getKpiGrowth('kpis.total_views.growth').toFixed(1)}% from last month
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Total Engagement */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Total Engagement</CardTitle>
                <Heart className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                {analyticsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-20 bg-gray-800" />
                    <Skeleton className="h-4 w-24 bg-gray-800" />
                  </div>
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatNumber(getKpiValue('kpis.total_engagement.value'))}
                    </div>
                    <p className={`text-xs flex items-center ${
                      getKpiGrowth('kpis.total_engagement.growth') >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      <ArrowUpRight className="h-3 w-3 mr-1" />
                      {getKpiGrowth('kpis.total_engagement.growth').toFixed(1)}% from last month
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Total GMV */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Total GMV</CardTitle>
                <CircleDollarSign className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                {analyticsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-20 bg-gray-800" />
                    <Skeleton className="h-4 w-24 bg-gray-800" />
                  </div>
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {formatCurrency(getKpiValue('kpis.total_gmv.value'))}
                    </div>
                    <p className={`text-xs flex items-center ${
                      getKpiGrowth('kpis.total_gmv.growth') >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      <ArrowUpRight className="h-3 w-3 mr-1" />
                      {getKpiGrowth('kpis.total_gmv.growth').toFixed(1)}% from last month
                    </p>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Active Creators */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Active Creators</CardTitle>
                <UserPlus className="h-4 w-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                {analyticsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-20 bg-gray-800" />
                    <Skeleton className="h-4 w-24 bg-gray-800" />
                  </div>
                ) : (
                  <>
                    <div className="text-2xl font-bold">
                      {getKpiValue('kpis.active_creators.value')}
                    </div>
                    <p className={`text-xs flex items-center ${
                      getKpiGrowth('kpis.active_creators.growth') >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      <ArrowUpRight className="h-3 w-3 mr-1" />
                      {getKpiGrowth('kpis.active_creators.growth').toFixed(1)}% from last month
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Financial Overview */}
            <Card className="lg:col-span-2 bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Financial Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-400">Total GMV Generated</p>
                      <p className="text-4xl font-bold">$124,350</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Revenue Growth</p>
                      <p className="text-2xl font-bold text-green-400 flex items-center">
                        +25% <ArrowUpRight className="h-5 w-5 ml-1" />
                      </p>
                    </div>
                  </div>
                  <div className="w-full sm:w-2/3 h-48">
                    <RevenueGrowthChart />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Campaign Progress */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Campaign Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {campaignProgress.map((campaign) => (
                  <div key={campaign.id}>
                    <div className="flex justify-between items-center mb-2">
                      <p className="text-sm font-medium truncate">{campaign.name}</p>
                      <p className={`text-xs font-bold uppercase ${getStatusTextColor(campaign.status)}`}>
                        {getStatusText(campaign.status)}
                      </p>
                    </div>
                    <Progress
                      value={campaign.progress_percentage}
                      className="h-2 mb-1"
                    />
                    <p className="text-xs text-gray-400">
                      {campaign.current_posts}/{campaign.target_posts} posts
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Bottom Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Top Creators */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Top Creators by Posts</CardTitle>
                <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">
                  View Details
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {performanceLoading ? (
                    <Skeleton className="h-10 w-full" />
                  ) : performanceError ? (
                    <p className="text-red-400">Error fetching creator performance.</p>
                  ) : (
                    safeCreatorPerformance.map((creator, index) => (
                      <div key={`creator-${creator.creator_id}-${index}`} className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-gray-700 overflow-hidden">
                          <img
                            src={creator.creator?.avatar_url || "/placeholder.svg"}
                            alt={`${creator.creator?.first_name} ${creator.creator?.last_name}`}
                            className="h-full w-full object-cover"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {creator.creator?.first_name} {creator.creator?.last_name}
                          </p>
                          <p className="text-xs text-gray-400">@{creator.creator?.username}</p>
                        </div>
                        <div className="text-sm font-bold">{creator.total_posts}</div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Posts per Day */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Posts per Day</CardTitle>
                <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">
                  View Details
                </Button>
              </CardHeader>
              <CardContent className="h-[300px]">
                <PostsPerDayChart />
              </CardContent>
            </Card>

            {/* Engagement Trends */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Engagement</CardTitle>
                <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">
                  View Details
                </Button>
              </CardHeader>
              <CardContent className="h-[300px]">
                <EngagementChart />
              </CardContent>
            </Card>
          </div>

          {/* Active Campaigns */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Active Campaigns</CardTitle>
              <Button 
                className="bg-purple-600 hover:bg-purple-700"
                onClick={() => setShowCampaignModal(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Campaign
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Campaign</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>GMV</TableHead>
                    <TableHead className="text-right">Creators</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {safeCampaigns.map((campaign) => (
                    <TableRow key={campaign.id} className="hover:bg-gray-800/50">
                      <TableCell className="font-medium">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewCampaignDetails(campaign)}
                        >
                          {campaign.name}
                        </Button>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="border-green-500 text-green-500">
                          {campaign.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-bold">${campaign.current_gmv || 0}</TableCell>
                      <TableCell className="text-right">{campaign.current_creators || 0}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Pause</DropdownMenuItem>
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Copy Link</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </main>
      </div>

      {/* Campaign Creation Modal */}
      <CampaignCreationModal isOpen={showCampaignModal} onClose={() => setShowCampaignModal(false)} />

      {/* Campaign Details Modal - Temporarily disabled due to type conflicts */}
      {/*selectedCampaign && (
        <CampaignDetailsModal
          campaign={selectedCampaign}
          onClose={() => {
            setSelectedCampaign(null)
            setShowCampaignDetailsModal(false)
          }}
        />
      )*/}
    </div>
  )
}
