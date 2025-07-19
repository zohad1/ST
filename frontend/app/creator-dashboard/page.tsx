"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronRight, Trophy, Eye, TrendingUp, Sparkles } from "lucide-react"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import { CampaignCard } from "@/components/campaign-card"
import { LeaderboardTable } from "@/components/leaderboard-table"
import { CampaignDetailsModal } from "@/components/campaign-details-modal"

// Import the backend hooks
import { useAuth } from "@/hooks/useAuth"
import { useCampaigns } from "@/hooks/useCampaigns"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function CreatorDashboard() {
  const [selectedCampaign, setSelectedCampaign] = useState<any>(null)
  const [dateRange, setDateRange] = useState("30d")
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const router = useRouter()

  // Use real backend data
  const { user, isLoading: authLoading, isAuthenticated } = useAuth()
  const { campaigns, loading: campaignsLoading, error: campaignsError } = useCampaigns({ status: "active" })

  // Protect the dashboard - redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      console.log("🚫 [CreatorDashboard] User not authenticated, redirecting to login")
      router.push("/auth/login")
    }
  }, [authLoading, isAuthenticated, router])

  // Debug: Log the campaigns structure
  console.log("🐛 [Debug] Campaigns response:", campaigns)
  console.log("🐛 [Debug] Is array?", Array.isArray(campaigns))
  console.log("🐛 [Debug] Type:", typeof campaigns)

  // Extract campaigns array from response (handle both array and object responses)
  const campaignsArray = Array.isArray(campaigns) ? campaigns : 
                        ((campaigns as any)?.data ? (Array.isArray((campaigns as any).data) ? (campaigns as any).data : []) : 
                        ((campaigns as any)?.campaigns ? (Array.isArray((campaigns as any).campaigns) ? (campaigns as any).campaigns : []) : []))

  // Calculate real stats from backend data
  const activeCampaigns = campaignsArray?.filter(c => c.status === 'active')?.length || 0
  const totalGMV = campaignsArray?.reduce((sum, c) => sum + (c.current_gmv || 0), 0) || 0
  const totalViews = campaignsArray?.reduce((sum, c) => sum + (c.total_deliverables || 0) * 50000, 0) || 0 // Estimate
  const bonusesEarned = Math.round(totalGMV * 0.1) // Estimate 10% bonus
  const gmvProgress = campaignsArray?.length > 0 ? 
    (campaignsArray.reduce((sum, c) => sum + ((c.current_gmv || 0) / (c.gmv_target || 1) * 100), 0) / campaignsArray.length) : 0

  // Transform backend campaigns to match UI expectations
  const transformedCampaigns = campaignsArray?.map(campaign => ({
    id: campaign.id,
    title: campaign.name,
    brand: campaign.brand_name || "Unknown Brand",
    logo: campaign.brand_logo || "/placeholder.svg?height=40&width=40",
    deliverables: campaign.total_deliverables || 1,
    completed: campaign.completed_deliverables || 0,
    gmv: campaign.current_gmv || 0,
    target: campaign.gmv_target || 1000,
    daysLeft: Math.ceil((new Date(campaign.end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)),
    status: campaign.status === 'active' ? 'active' : 
            campaign.status === 'completed' ? 'completed' : 
            campaign.status === 'paused' ? 'pending' : 'active',
    priority: 1,
  })) || []

  // Sort campaigns by priority (overdue first, then active, then completed)
  const sortedCampaigns = transformedCampaigns.sort((a, b) => {
    if (a.daysLeft < 0 && b.daysLeft >= 0) return -1
    if (a.daysLeft >= 0 && b.daysLeft < 0) return 1
    if (a.status === 'active' && b.status !== 'active') return -1
    if (a.status !== 'active' && b.status === 'active') return 1
    return 0
  })

  // Loading states
  if (authLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-400">Checking authentication...</p>
        </div>
      </div>
    )
  }

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  if (campaignsLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Error states - Show fallback dashboard if campaign service is not available
  if (campaignsError) {
    return (
      <div className="min-h-screen bg-black text-white">
        <CreatorSidebar 
          isMobileOpen={isMobileSidebarOpen} 
          onMobileClose={() => setIsMobileSidebarOpen(false)} 
        />

        <div className="lg:ml-60 min-h-screen">
          <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />

          <main className="p-6 space-y-6">
            {/* Welcome Message */}
            <div className="text-center py-12">
              <h1 className="text-3xl font-bold text-white mb-4">Welcome to Your Dashboard!</h1>
              <p className="text-gray-400 mb-6">Your account is ready. Campaign service will be available soon.</p>
              
              {/* Sample Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-300">Account Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-400">Active</div>
                    <div className="text-xs text-gray-400">Ready to start</div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-300">Profile Complete</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-400">100%</div>
                    <div className="text-xs text-gray-400">All set up</div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-300">Next Steps</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-400">Ready</div>
                    <div className="text-xs text-gray-400">Wait for campaigns</div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  // Sample leaderboard data (you can replace this with real data later)
  const leaderboardData = [
    { rank: 1, name: "Emma Rodriguez", avatar: "/placeholder.svg?height=32&width=32", gmv: 8540, growth: 23 },
    { rank: 2, name: "Marcus Chen", avatar: "/placeholder.svg?height=32&width=32", gmv: 7890, growth: 18 },
    { rank: 3, name: "Sophia Kim", avatar: "/placeholder.svg?height=32&width=32", gmv: 7234, growth: 15 },
    { rank: 4, name: user?.display_name || user?.username || "You", avatar: "/placeholder.svg?height=32&width=32", gmv: Math.round(totalGMV), growth: 12, isCurrentUser: true },
    { rank: 5, name: "David Park", avatar: "/placeholder.svg?height=32&width=32", gmv: 6123, growth: 8 },
  ]

  return (
    <div className="min-h-screen bg-black text-white">
      <CreatorSidebar 
        isMobileOpen={isMobileSidebarOpen} 
        onMobileClose={() => setIsMobileSidebarOpen(false)} 
      />

      <div className="lg:ml-60 min-h-screen">
        <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />

        <main className="p-6 space-y-6">
          {/* Performance Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">Active Campaigns</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{activeCampaigns}</div>
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  {activeCampaigns > 0 ? '+' : ''}0% from last month
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">Total GMV</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">${totalGMV.toLocaleString()}</div>
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  +15% from last month
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">Total Views</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{(totalViews / 1000000).toFixed(1)}M</div>
                <div className="flex items-center gap-1 text-xs text-green-400">
                  <Eye className="h-3 w-3" />
                  +12% engagement
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">Bonuses Earned</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">${bonusesEarned.toLocaleString()}</div>
                <div className="flex items-center gap-1 text-xs text-yellow-400">
                  <Sparkles className="h-3 w-3" />
                  3 bonus tiers hit
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Campaigns Section */}
            <div className="lg:col-span-2">
              <Tabs defaultValue="active" className="space-y-6">
                <div className="flex items-center justify-between">
                  <TabsList className="bg-gray-900 border border-gray-800">
                    <TabsTrigger value="active" className="data-[state=active]:bg-purple-600">
                      Active ({activeCampaigns})
                    </TabsTrigger>
                    <TabsTrigger value="completed" className="data-[state=active]:bg-purple-600">
                      Completed
                    </TabsTrigger>
                    <TabsTrigger value="all" className="data-[state=active]:bg-purple-600">
                      All Campaigns
                    </TabsTrigger>
                  </TabsList>

                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger className="w-32 bg-gray-900 border-gray-800">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">Last 7 days</SelectItem>
                      <SelectItem value="30d">Last 30 days</SelectItem>
                      <SelectItem value="90d">Last 90 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <TabsContent value="active" className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {sortedCampaigns.filter(c => c.status === 'active').length > 0 ? (
                    sortedCampaigns
                      .filter(campaign => campaign.status === 'active')
                      .map((campaign) => (
                        <CampaignCard
                          key={campaign.id}
                          title={campaign.title}
                          brand={campaign.brand}
                          logo={campaign.logo}
                          deliverables={campaign.deliverables}
                          completed={campaign.completed}
                          gmv={campaign.gmv}
                          target={campaign.target}
                          daysLeft={campaign.daysLeft}
                          status={campaign.status}
                          onViewDetails={() => setSelectedCampaign(campaign)}
                        />
                      ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-400">No active campaigns found.</p>
                      <p className="text-sm text-gray-500 mt-2">Check back later or browse available campaigns.</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="completed" className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {sortedCampaigns.filter(c => c.status === 'completed').length > 0 ? (
                    sortedCampaigns
                      .filter(campaign => campaign.status === 'completed')
                      .map((campaign) => (
                        <CampaignCard
                          key={campaign.id}
                          title={campaign.title}
                          brand={campaign.brand}
                          logo={campaign.logo}
                          deliverables={campaign.deliverables}
                          completed={campaign.completed}
                          gmv={campaign.gmv}
                          target={campaign.target}
                          daysLeft={campaign.daysLeft}
                          status={campaign.status}
                          onViewDetails={() => setSelectedCampaign(campaign)}
                        />
                      ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-400">No completed campaigns yet.</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="all" className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {sortedCampaigns.length > 0 ? (
                    sortedCampaigns.map((campaign) => (
                      <CampaignCard
                        key={campaign.id}
                        title={campaign.title}
                        brand={campaign.brand}
                        logo={campaign.logo}
                        deliverables={campaign.deliverables}
                        completed={campaign.completed}
                        gmv={campaign.gmv}
                        target={campaign.target}
                        daysLeft={campaign.daysLeft}
                        status={campaign.status}
                        onViewDetails={() => setSelectedCampaign(campaign)}
                      />
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-400">No campaigns found.</p>
                      <p className="text-sm text-gray-500 mt-2">Start by applying to campaigns that match your profile.</p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* GMV Progress */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Trophy className="h-5 w-5 text-yellow-400" />
                    Monthly GMV Target
                  </CardTitle>
                  <CardDescription>Track your progress towards monthly goals</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Progress</span>
                      <span className="text-white font-medium">{Math.round(gmvProgress)}%</span>
                    </div>
                    <Progress value={gmvProgress} className="h-2" />
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">${Math.round(totalGMV).toLocaleString()}</div>
                    <div className="text-sm text-gray-400">of ${Math.round(totalGMV * 1.5).toLocaleString()} goal</div>
                  </div>
                </CardContent>
              </Card>

              {/* Leaderboard */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Trophy className="h-5 w-5 text-yellow-400" />
                    Leaderboard
                  </CardTitle>
                  <CardDescription>Top performers this month</CardDescription>
                </CardHeader>
                <CardContent>
                  <LeaderboardTable data={leaderboardData} />
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>

      {/* Campaign Details Modal */}
      {selectedCampaign && (
        <CampaignDetailsModal
          campaign={selectedCampaign}
          isOpen={!!selectedCampaign}
          onClose={() => setSelectedCampaign(null)}
        />
      )}
    </div>
  )
}
