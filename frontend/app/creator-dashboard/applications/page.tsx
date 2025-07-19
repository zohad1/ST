"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import {
  Search,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Calendar,
  DollarSign,
  Users,
  AlertCircle,
  Hourglass,
  AlertTriangle,
  RefreshCw,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/hooks/useAuth"
import { useMyApplications, type Application } from "@/hooks/useMyApplications"
import { toast } from "@/components/ui/use-toast"

// Transform backend application to frontend format
interface TransformedApplication {
  id: string
  campaignId: string
  campaignName: string
  brandName: string
  brandLogo: string
  appliedDate: string
  status: "pending" | "approved" | "rejected" | "interview" | "waitlist"
  deadline: string
  budget: number
  deliverables: number
  category: string
  notes?: string
}

export default function CreatorApplicationsPage() {
  const { user, isAuthenticated } = useAuth()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  
  // Get applications data from the hook
  const { applications: rawApplications, loading, error, refetch } = useMyApplications()

  // Transform backend applications to frontend format
  const transformApplication = (backendApp: Application): TransformedApplication => {
    const campaign = backendApp.campaign || {}
    const startDate = new Date(campaign.start_date || Date.now())
    const endDate = new Date(campaign.end_date || Date.now() + 30 * 24 * 60 * 60 * 1000)
    
    return {
      id: backendApp.id,
      campaignId: backendApp.campaign_id,
      campaignName: campaign.name || "Untitled Campaign",
      brandName: campaign.brand_name || "Unknown Brand", 
      brandLogo: campaign.brand_logo || campaign.thumbnail_url || "/placeholder.svg",
      appliedDate: backendApp.applied_at,
      status: backendApp.status,
      deadline: endDate.toISOString(),
      budget: campaign.budget || 0,
      deliverables: campaign.min_deliverables_per_creator || 1,
      category: campaign.category || campaign.type || "General",
      notes: backendApp.rejection_reason || backendApp.review_notes,
    }
  }

  // Transform applications using the helper function
  const applications = rawApplications?.map(transformApplication) || []

  const filteredApplications = applications.filter(app => {
    const matchesSearch = 
      app.campaignName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.brandName.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === "all" || app.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const getStatusConfig = (status: TransformedApplication["status"]) => {
    switch (status) {
      case "pending":
        return {
          badge: <Badge className="bg-yellow-600 hover:bg-yellow-700">Pending</Badge>,
          icon: <Clock className="h-4 w-4 text-yellow-500" />,
          color: "text-yellow-500",
          bgColor: "bg-yellow-500/10",
          borderColor: "border-yellow-500/30",
        }
      case "approved":
        return {
          badge: <Badge className="bg-green-600 hover:bg-green-700">Approved</Badge>,
          icon: <CheckCircle className="h-4 w-4 text-green-500" />,
          color: "text-green-500",
          bgColor: "bg-green-500/10",
          borderColor: "border-green-500/30",
        }
      case "rejected":
        return {
          badge: <Badge className="bg-red-600 hover:bg-red-700">Rejected</Badge>,
          icon: <XCircle className="h-4 w-4 text-red-500" />,
          color: "text-red-500",
          bgColor: "bg-red-500/10",
          borderColor: "border-red-500/30",
        }
      case "interview":
        return {
          badge: <Badge className="bg-blue-600 hover:bg-blue-700">Interview</Badge>,
          icon: <Users className="h-4 w-4 text-blue-500" />,
          color: "text-blue-500",
          bgColor: "bg-blue-500/10",
          borderColor: "border-blue-500/30",
        }
      case "waitlist":
        return {
          badge: <Badge className="bg-purple-600 hover:bg-purple-700">Waitlist</Badge>,
          icon: <Hourglass className="h-4 w-4 text-purple-500" />,
          color: "text-purple-500",
          bgColor: "bg-purple-500/10",
          borderColor: "border-purple-500/30",
        }
      default:
        return {
          badge: <Badge className="bg-gray-600 hover:bg-gray-700">Unknown</Badge>,
          icon: <AlertCircle className="h-4 w-4 text-gray-500" />,
          color: "text-gray-500",
          bgColor: "bg-gray-500/10",
          borderColor: "border-gray-500/30",
        }
    }
  }

  // Calculate stats
  const stats = {
    total: filteredApplications.length,
    pending: filteredApplications.filter(app => app.status === 'pending').length,
    approved: filteredApplications.filter(app => app.status === 'approved').length,
    rejected: filteredApplications.filter(app => app.status === 'rejected').length,
    successRate: Math.round((filteredApplications.filter(app => app.status === 'approved').length / Math.max(filteredApplications.length, 1)) * 100),
  }

  const getDaysAgo = (dateString: string) => {
    const days = Math.floor((new Date().getTime() - new Date(dateString).getTime()) / (1000 * 60 * 60 * 24))
    return days === 0 ? "Today" : days === 1 ? "1 day ago" : `${days} days ago`
  }

  const handleRetry = () => {
    refetch()
    toast({
      title: "Refreshing",
      description: "Fetching latest applications...",
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white">
        <CreatorSidebar 
          isMobileOpen={isMobileSidebarOpen} 
          onMobileClose={() => setIsMobileSidebarOpen(false)} 
        />
        <div className="lg:ml-60 min-h-screen">
          <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />
          <main className="p-6">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Loading your applications...</p>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

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
            <h1 className="text-3xl font-bold mb-2">Applications</h1>
            <p className="text-gray-400 text-lg">Track your campaign applications and their status</p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 bg-red-900/20 border border-red-600/30 rounded-lg p-4 flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-red-500 font-medium">Error Loading Applications</p>
                <p className="text-red-400/80 text-sm">{error}</p>
              </div>
              <Button 
                onClick={handleRetry} 
                variant="outline" 
                size="sm"
                className="border-red-600/30 text-red-500 hover:bg-red-600/10"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          )}

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Total Applications</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
                <p className="text-xs text-gray-400 mt-1">All time</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Pending Review</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-400">{stats.pending}</div>
                <p className="text-xs text-gray-400 mt-1">Awaiting response</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Approved</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-400">{stats.approved}</div>
                <p className="text-xs text-gray-400 mt-1">Successful applications</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-400">{stats.successRate}%</div>
                <p className="text-xs text-gray-400 mt-1">Approval rate</p>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search applications..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-gray-900 border-gray-800"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px] bg-gray-900 border-gray-800">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-800">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="interview">Interview</SelectItem>
                <SelectItem value="waitlist">Waitlist</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Applications Tabs */}
          <Tabs defaultValue="all" className="space-y-6">
            <TabsList className="bg-gray-900 border-gray-800">
              <TabsTrigger value="all" className="data-[state=active]:bg-purple-600">
                All Applications
              </TabsTrigger>
              <TabsTrigger value="pending" className="data-[state=active]:bg-purple-600">
                Pending ({stats.pending})
              </TabsTrigger>
              <TabsTrigger value="approved" className="data-[state=active]:bg-purple-600">
                Approved ({stats.approved})
              </TabsTrigger>
              <TabsTrigger value="rejected" className="data-[state=active]:bg-purple-600">
                Rejected ({stats.rejected})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              {filteredApplications.length > 0 ? (
                filteredApplications.map((application) => {
                  const config = getStatusConfig(application.status)
                  return (
                    <Card
                      key={application.id}
                      className={cn(
                        "bg-gray-900 border-gray-800 hover:border-purple-500/50 transition-all duration-300",
                        config.borderColor
                      )}
                    >
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-4">
                            <div className="h-12 w-12 rounded-lg bg-gray-800 overflow-hidden">
                              <img
                                src={application.brandLogo}
                                alt={application.brandName}
                                className="h-full w-full object-cover"
                              />
                            </div>
                            <div>
                              <h3 className="font-semibold text-lg">{application.campaignName}</h3>
                              <p className="text-gray-400 text-sm">{application.brandName}</p>
                              <p className="text-gray-500 text-xs">Applied {getDaysAgo(application.appliedDate)}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {config.icon}
                            {config.badge}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div className="flex items-center gap-2 text-sm">
                            <DollarSign className="h-4 w-4 text-green-400" />
                            <span className="text-gray-300">
                              {application.budget > 0 ? `$${application.budget.toLocaleString()}` : 'TBD'}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <FileText className="h-4 w-4 text-purple-400" />
                            <span className="text-gray-300">{application.deliverables} deliverables</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-blue-400" />
                            <span className="text-gray-300">Deadline: {new Date(application.deadline).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Badge variant="outline" className="text-xs">
                              {application.category}
                            </Badge>
                          </div>
                        </div>

                        {application.notes && (
                          <div className={cn("p-3 rounded-lg border text-sm mb-4", config.bgColor, config.borderColor)}>
                            <div className="flex items-start gap-2">
                              <AlertCircle className={cn("h-4 w-4 mt-0.5", config.color)} />
                              <div>
                                <p className="font-medium mb-1">Notes:</p>
                                <p className="text-gray-300">{application.notes}</p>
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="border-gray-600 hover:bg-gray-800">
                            <Eye className="h-4 w-4 mr-2" />
                            View Campaign
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No applications found</h3>
                  <p className="text-gray-500">
                    {searchQuery ? "Try adjusting your search or filters" : "Apply to campaigns to see them here"}
                  </p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="pending" className="space-y-4">
              {filteredApplications.filter(app => app.status === 'pending').map((application) => {
                const config = getStatusConfig(application.status)
                return (
                  <Card key={application.id} className="bg-gray-900 border-gray-800">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">{application.campaignName}</h3>
                          <p className="text-sm text-gray-400">{application.brandName}</p>
                        </div>
                        {config.badge}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </TabsContent>

            <TabsContent value="approved" className="space-y-4">
              {filteredApplications.filter(app => app.status === 'approved').map((application) => {
                const config = getStatusConfig(application.status)
                return (
                  <Card key={application.id} className="bg-gray-900 border-gray-800">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">{application.campaignName}</h3>
                          <p className="text-sm text-gray-400">{application.brandName}</p>
                        </div>
                        {config.badge}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </TabsContent>

            <TabsContent value="rejected" className="space-y-4">
              {filteredApplications.filter(app => app.status === 'rejected').map((application) => {
                const config = getStatusConfig(application.status)
                return (
                  <Card key={application.id} className="bg-gray-900 border-gray-800">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="font-semibold">{application.campaignName}</h3>
                          <p className="text-sm text-gray-400">{application.brandName}</p>
                        </div>
                        {config.badge}
                      </div>
                      {application.notes && (
                        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm">
                          <p className="text-red-400 font-medium mb-1">Reason:</p>
                          <p className="text-gray-300">{application.notes}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )
              })}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
} 