"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import {
  TrendingUp,
  TrendingDown,
  Eye,
  Heart,
  Share2,
  MessageCircle,
  Users,
  DollarSign,
  Target,
  BarChart3,
  PieChart,
  Calendar,
  Download,
  ArrowUp,
  ArrowDown,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCard {
  title: string
  value: string | number
  change: number
  changeLabel: string
  icon: React.ReactNode
  color: string
}

interface CampaignMetric {
  id: string
  name: string
  brand: string
  views: number
  engagement: number
  clicks: number
  conversions: number
  revenue: number
  startDate: string
  endDate: string
}

const mockCampaignMetrics: CampaignMetric[] = [
  {
    id: "1",
    name: "Summer Fashion Collection",
    brand: "StyleBrand",
    views: 145000,
    engagement: 8.5,
    clicks: 1250,
    conversions: 89,
    revenue: 4500,
    startDate: "2025-06-01",
    endDate: "2025-06-30",
  },
  {
    id: "2",
    name: "Tech Gadget Pro Launch",
    brand: "TechCorp",
    views: 89000,
    engagement: 12.3,
    clicks: 2100,
    conversions: 156,
    revenue: 7800,
    startDate: "2025-06-10",
    endDate: "2025-07-10",
  },
  {
    id: "3",
    name: "Beauty Essentials Kit",
    brand: "BeautyBrand",
    views: 67000,
    engagement: 15.2,
    clicks: 980,
    conversions: 67,
    revenue: 3400,
    startDate: "2025-06-15",
    endDate: "2025-07-15",
  },
]

export default function CreatorAnalyticsPage() {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [timeRange, setTimeRange] = useState("30d")

  const overviewMetrics: MetricCard[] = [
    {
      title: "Total Views",
      value: "2.4M",
      change: 12.5,
      changeLabel: "vs last month",
      icon: <Eye className="h-5 w-5" />,
      color: "text-blue-400",
    },
    {
      title: "Engagement Rate",
      value: "8.9%",
      change: 2.1,
      changeLabel: "vs last month",
      icon: <Heart className="h-5 w-5" />,
      color: "text-red-400",
    },
    {
      title: "Total Earnings",
      value: "$18,650",
      change: 23.8,
      changeLabel: "vs last month",
      icon: <DollarSign className="h-5 w-5" />,
      color: "text-green-400",
    },
    {
      title: "Click-through Rate",
      value: "3.2%",
      change: -0.8,
      changeLabel: "vs last month",
      icon: <Target className="h-5 w-5" />,
      color: "text-purple-400",
    },
  ]

  const socialMetrics = {
    followers: {
      current: 125400,
      growth: 2850,
      growthRate: 2.3,
    },
    avgLikes: {
      current: 8950,
      growth: 450,
      growthRate: 5.3,
    },
    avgComments: {
      current: 320,
      growth: -15,
      growthRate: -4.5,
    },
    avgShares: {
      current: 180,
      growth: 25,
      growthRate: 16.1,
    },
  }

  const platformBreakdown = [
    { platform: "Instagram", percentage: 45, color: "bg-pink-500" },
    { platform: "TikTok", percentage: 30, color: "bg-purple-500" },
    { platform: "YouTube", percentage: 20, color: "bg-red-500" },
    { platform: "Twitter", percentage: 5, color: "bg-blue-500" },
  ]

  const contentPerformance = [
    { type: "Videos", count: 24, avgViews: 95000, engagement: 12.5 },
    { type: "Images", count: 42, avgViews: 65000, engagement: 8.9 },
    { type: "Stories", count: 156, avgViews: 25000, engagement: 15.2 },
    { type: "Reels", count: 18, avgViews: 180000, engagement: 18.7 },
  ]

  return (
    <div className="min-h-screen bg-black text-white">
      <CreatorSidebar 
        isMobileOpen={isMobileSidebarOpen} 
        onMobileClose={() => setIsMobileSidebarOpen(false)} 
      />

      <div className="lg:ml-60 min-h-screen">
        <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />

        <main className="p-6">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">Performance Analytics</h1>
                <p className="text-gray-400 text-lg">Track your content performance and engagement metrics</p>
              </div>
              <div className="flex items-center gap-3">
                <Select value={timeRange} onValueChange={setTimeRange}>
                  <SelectTrigger className="w-32 bg-gray-900 border-gray-800">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-900 border-gray-800">
                    <SelectItem value="7d">Last 7 days</SelectItem>
                    <SelectItem value="30d">Last 30 days</SelectItem>
                    <SelectItem value="90d">Last 90 days</SelectItem>
                    <SelectItem value="1y">Last year</SelectItem>
                  </SelectContent>
                </Select>
                <Button variant="outline" size="sm" className="border-purple-500 text-purple-400 bg-transparent">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </div>

          {/* Overview Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {overviewMetrics.map((metric, index) => (
              <Card key={index} className="bg-gray-900 border-gray-800">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400 flex items-center gap-2">
                    <span className={metric.color}>{metric.icon}</span>
                    {metric.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold mb-1">{metric.value}</div>
                  <div className="flex items-center gap-1 text-xs">
                    {metric.change > 0 ? (
                      <ArrowUp className="h-3 w-3 text-green-400" />
                    ) : (
                      <ArrowDown className="h-3 w-3 text-red-400" />
                    )}
                    <span className={metric.change > 0 ? "text-green-400" : "text-red-400"}>
                      {Math.abs(metric.change)}%
                    </span>
                    <span className="text-gray-400">{metric.changeLabel}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="bg-gray-900 border-gray-800">
              <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600">
                Overview
              </TabsTrigger>
              <TabsTrigger value="campaigns" className="data-[state=active]:bg-purple-600">
                Campaign Performance
              </TabsTrigger>
              <TabsTrigger value="content" className="data-[state=active]:bg-purple-600">
                Content Analytics
              </TabsTrigger>
              <TabsTrigger value="audience" className="data-[state=active]:bg-purple-600">
                Audience Insights
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Social Media Growth */}
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5 text-purple-400" />
                      Social Media Growth
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-400">Followers</p>
                        <p className="text-2xl font-bold">{socialMetrics.followers.current.toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-1">
                          <ArrowUp className="h-4 w-4 text-green-400" />
                          <span className="text-green-400">+{socialMetrics.followers.growth}</span>
                        </div>
                        <p className="text-xs text-gray-400">+{socialMetrics.followers.growthRate}%</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-gray-400">Avg Likes</p>
                        <p className="font-semibold">{socialMetrics.avgLikes.current.toLocaleString()}</p>
                        <div className="flex items-center gap-1">
                          <ArrowUp className="h-3 w-3 text-green-400" />
                          <span className="text-xs text-green-400">{socialMetrics.avgLikes.growthRate}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400">Avg Comments</p>
                        <p className="font-semibold">{socialMetrics.avgComments.current}</p>
                        <div className="flex items-center gap-1">
                          <ArrowDown className="h-3 w-3 text-red-400" />
                          <span className="text-xs text-red-400">{Math.abs(socialMetrics.avgComments.growthRate)}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400">Avg Shares</p>
                        <p className="font-semibold">{socialMetrics.avgShares.current}</p>
                        <div className="flex items-center gap-1">
                          <ArrowUp className="h-3 w-3 text-green-400" />
                          <span className="text-xs text-green-400">{socialMetrics.avgShares.growthRate}%</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Platform Breakdown */}
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="h-5 w-5 text-purple-400" />
                      Platform Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {platformBreakdown.map((platform, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{platform.platform}</span>
                          <span>{platform.percentage}%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div
                            className={cn("h-2 rounded-full", platform.color)}
                            style={{ width: `${platform.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Content Performance */}
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-purple-400" />
                      Content Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {contentPerformance.map((content, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <div>
                            <p className="font-medium">{content.type}</p>
                            <p className="text-sm text-gray-400">{content.count} posts</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">{content.avgViews.toLocaleString()}</p>
                            <p className="text-sm text-gray-400">avg views</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-purple-400">{content.engagement}%</p>
                            <p className="text-sm text-gray-400">engagement</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Achievements */}
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-purple-400" />
                      Recent Achievements
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <div className="h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center">
                        <TrendingUp className="h-4 w-4 text-green-400" />
                      </div>
                      <div>
                        <p className="font-medium">100K Followers Milestone</p>
                        <p className="text-xs text-gray-400">Achieved 3 days ago</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                      <div className="h-8 w-8 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <Eye className="h-4 w-4 text-purple-400" />
                      </div>
                      <div>
                        <p className="font-medium">Viral Post - 500K Views</p>
                        <p className="text-xs text-gray-400">Summer Fashion lookbook</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <div className="h-8 w-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                        <DollarSign className="h-4 w-4 text-blue-400" />
                      </div>
                      <div>
                        <p className="font-medium">Top Performer Badge</p>
                        <p className="text-xs text-gray-400">Tech Gadget campaign</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="campaigns">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Campaign Performance Comparison</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {mockCampaignMetrics.map((campaign) => (
                        <div key={campaign.id} className="p-4 bg-gray-800/50 rounded-lg">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-semibold">{campaign.name}</h3>
                              <p className="text-sm text-gray-400">{campaign.brand}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(campaign.startDate).toLocaleDateString()} - {new Date(campaign.endDate).toLocaleDateString()}
                              </p>
                            </div>
                            <Badge className="bg-purple-600">${campaign.revenue.toLocaleString()}</Badge>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="text-gray-400">Views</p>
                              <p className="font-semibold">{campaign.views.toLocaleString()}</p>
                            </div>
                            <div>
                              <p className="text-gray-400">Engagement</p>
                              <p className="font-semibold">{campaign.engagement}%</p>
                            </div>
                            <div>
                              <p className="text-gray-400">Clicks</p>
                              <p className="font-semibold">{campaign.clicks.toLocaleString()}</p>
                            </div>
                            <div>
                              <p className="text-gray-400">Conversions</p>
                              <p className="font-semibold">{campaign.conversions}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="content">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Top Performing Content</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                      <div className="h-12 w-12 bg-gray-800 rounded-lg"></div>
                      <div className="flex-1">
                        <p className="font-medium">Summer Outfit Haul</p>
                        <p className="text-sm text-gray-400">Instagram Reel</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">847K views</p>
                        <p className="text-sm text-green-400">+245%</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                      <div className="h-12 w-12 bg-gray-800 rounded-lg"></div>
                      <div className="flex-1">
                        <p className="font-medium">Tech Unboxing Review</p>
                        <p className="text-sm text-gray-400">YouTube Video</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">523K views</p>
                        <p className="text-sm text-green-400">+189%</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                      <div className="h-12 w-12 bg-gray-800 rounded-lg"></div>
                      <div className="flex-1">
                        <p className="font-medium">Beauty Tutorial</p>
                        <p className="text-sm text-gray-400">TikTok Video</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">412K views</p>
                        <p className="text-sm text-green-400">+156%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Engagement Trends</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Heart className="h-4 w-4 text-red-400" />
                        <span className="text-sm">Likes</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">425K</p>
                        <p className="text-xs text-green-400">+12.5%</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4 text-blue-400" />
                        <span className="text-sm">Comments</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">18.2K</p>
                        <p className="text-xs text-red-400">-2.1%</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Share2 className="h-4 w-4 text-green-400" />
                        <span className="text-sm">Shares</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">8.9K</p>
                        <p className="text-xs text-green-400">+18.7%</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Eye className="h-4 w-4 text-purple-400" />
                        <span className="text-sm">Story Views</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">156K</p>
                        <p className="text-xs text-green-400">+7.3%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="audience">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Audience Demographics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Age Groups</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">18-24</span>
                          <span className="text-sm">32%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div className="bg-purple-500 h-2 rounded-full" style={{ width: '32%' }} />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">25-34</span>
                          <span className="text-sm">45%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{ width: '45%' }} />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">35-44</span>
                          <span className="text-sm">18%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '18%' }} />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">45+</span>
                          <span className="text-sm">5%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '5%' }} />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Top Locations</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>United States</span>
                      <span className="font-semibold">42%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Canada</span>
                      <span className="font-semibold">18%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>United Kingdom</span>
                      <span className="font-semibold">12%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Australia</span>
                      <span className="font-semibold">8%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Germany</span>
                      <span className="font-semibold">6%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Other</span>
                      <span className="font-semibold">14%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
} 