"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import {
  Search,
  Upload,
  Clock,
  CheckCircle,
  AlertCircle,
  Eye,
  Calendar,
  FileText,
  Video,
  Image,
  Target,
  TrendingUp,
  RefreshCw,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useMyApplications } from "@/hooks/useMyApplications"
import { campaignServiceClient } from "@/lib/api/client"
import { toast } from "@/components/ui/use-toast"

interface Deliverable {
  id: string
  title: string
  description: string
  type: string
  requirements: string[]
  dueDate: string
  submittedDate?: string
  status: string
  feedback?: string
  submissionUrl?: string
  priority?: string
}

export default function CreatorDeliverablesPage() {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>("")
  const [deliverables, setDeliverables] = useState<Deliverable[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showSubmitModal, setShowSubmitModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submissionData, setSubmissionData] = useState({
    title: "",
    description: "",
    content_url: "",
    content_type: "",
    hashtags: "",
  })

  // Fetch campaigns the creator is part of
  const { applications, loading: campaignsLoading, error: campaignsError } = useMyApplications()
  const campaigns = applications
    .filter(app => app.campaign && (app.status === "approved" || app.status === "pending"))
    .map(app => app.campaign)
    .filter((c, i, arr) => c && arr.findIndex(x => x?.id === c?.id) === i) // unique by id
    .filter(Boolean) as NonNullable<typeof applications[0]["campaign"]>[]

  // Set default campaign
  useEffect(() => {
    if (campaigns.length > 0 && !selectedCampaignId) {
      setSelectedCampaignId(campaigns[0].id)
    }
  }, [campaigns, selectedCampaignId])

  // Fetch deliverables for selected campaign
  useEffect(() => {
    const fetchDeliverables = async () => {
      if (!selectedCampaignId) return
      setLoading(true)
      setError(null)
      try {
        const response = await campaignServiceClient.get<any>(`/api/v1/deliverables/campaign/${selectedCampaignId}/creator`)
        let data: any[] = []
        if (Array.isArray(response.data)) {
          data = response.data
        } else if (response.data?.deliverables && Array.isArray(response.data.deliverables)) {
          data = response.data.deliverables
        } else if (response.data?.data && Array.isArray(response.data.data)) {
          data = response.data.data
        }
        setDeliverables(
          data.map((d: any) => ({
            id: d.id,
            title: d.title || d.content_type || `Deliverable #${d.deliverable_number}`,
            description: d.description || d.post_caption || "",
            type: d.content_type || "other",
            requirements: d.hashtags_used || [],
            dueDate: d.due_date || d.created_at,
            submittedDate: d.submitted_at,
            status: d.status,
            feedback: d.feedback,
            submissionUrl: d.tiktok_post_url || d.content_url,
            priority: d.priority || "medium",
          }))
        )
      } catch (err: any) {
        setError(err.message || "Failed to load deliverables")
        setDeliverables([])
      } finally {
        setLoading(false)
      }
    }
    if (selectedCampaignId) fetchDeliverables()
  }, [selectedCampaignId])

  // Submit new deliverable
  const handleSubmitDeliverable = async () => {
    if (!submissionData.title || !submissionData.content_url) {
      toast({
        title: "Missing required fields",
        description: "Please provide a title and content URL.",
        variant: "destructive",
      })
      return
    }
    setSubmitting(true)
    try {
      // Find the application for this campaign
      const application = applications.find(app => app.campaign_id === selectedCampaignId)
      if (!application) {
        toast({
          title: "Error",
          description: "No application found for this campaign",
          variant: "destructive"
        })
        return
      }

      const payload = {
        title: submissionData.title,
        description: submissionData.description,
        content_url: submissionData.content_url,
        content_type: submissionData.content_type,
        hashtags: submissionData.hashtags.split(',').map(tag => tag.trim()),
        campaign_id: selectedCampaignId,
        application_id: application.id,
        deliverable_number: 1 // For now, we'll use 1 as the first deliverable
      }
      
      console.log('Submitting deliverable with payload:', payload)
      
      const response = await campaignServiceClient.post(`/api/v1/deliverables/`, payload)
      
      console.log('Response received:', response)

      if (response.success) {
        toast({
          title: "Success",
          description: "Deliverable submitted successfully",
        })
        setShowSubmitModal(false)
        setSubmissionData({ title: "", description: "", content_url: "", content_type: "", hashtags: "" })
        // Refresh deliverables by refetching
        if (selectedCampaignId) {
          // Trigger a refetch by updating the selected campaign ID
          const currentId = selectedCampaignId
          setSelectedCampaignId("")
          setTimeout(() => setSelectedCampaignId(currentId), 100)
        }
      } else {
        throw new Error(response.error || "Failed to submit deliverable")
      }
    } catch (err: any) {
      toast({
        title: "Submission failed",
        description: err.message || "Failed to submit deliverable.",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const filteredDeliverables = deliverables.filter(deliverable => {
    const matchesSearch =
      deliverable.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === "all" || deliverable.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "pending":
      case "submitted":
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
          icon: <AlertCircle className="h-4 w-4 text-red-500" />,
          color: "text-red-500",
          bgColor: "bg-red-500/10",
          borderColor: "border-red-500/30",
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

  return (
    <div className="min-h-screen bg-black text-white">
      <CreatorSidebar
        isMobileOpen={isMobileSidebarOpen}
        onMobileClose={() => setIsMobileSidebarOpen(false)}
      />
      <div className="lg:ml-60 min-h-screen">
        <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />
        <main className="p-6">
          <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">Deliverables</h1>
              <p className="text-gray-400 text-lg">Submit and track your campaign deliverables</p>
            </div>
            <div className="flex gap-2 items-center">
              <Select value={selectedCampaignId} onValueChange={setSelectedCampaignId}>
                <SelectTrigger className="w-[220px] bg-gray-900 border-gray-800">
                  <SelectValue placeholder="Select Campaign" />
                </SelectTrigger>
                <SelectContent className="bg-gray-900 border-gray-800">
                  {campaigns.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button className="bg-purple-600 hover:bg-purple-700" onClick={() => setShowSubmitModal(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Submit Deliverable
              </Button>
            </div>
          </div>

          {/* Error/Loading States */}
          {(loading || campaignsLoading) && (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
              <p className="text-gray-400 ml-4">Loading...</p>
            </div>
          )}
          {error && (
            <div className="mb-6 bg-red-900/20 border border-red-600/30 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-red-500 font-medium">Error Loading Deliverables</p>
                <p className="text-red-400/80 text-sm">{error}</p>
              </div>
              <Button onClick={() => setSelectedCampaignId(selectedCampaignId)} variant="outline" size="sm" className="border-red-600/30 text-red-500 hover:bg-red-600/10">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          )}

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search deliverables..."
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
                <SelectItem value="submitted">Submitted</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Deliverables List */}
          <div className="space-y-4">
            {filteredDeliverables.length > 0 ? (
              filteredDeliverables.map((deliverable) => {
                const config = getStatusConfig(deliverable.status)
                return (
                  <Card key={deliverable.id} className={cn("bg-gray-900 border-gray-800", config.borderColor)}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-lg mb-1">{deliverable.title}</h3>
                          <p className="text-gray-400 text-sm mb-2">Due: {new Date(deliverable.dueDate).toLocaleDateString()}</p>
                          <p className="text-gray-300 text-sm mb-2">{deliverable.description}</p>
                          <div className="flex flex-wrap gap-1 mb-2">
                            {deliverable.requirements.map((tag, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          {deliverable.feedback && (
                            <div className="p-3 rounded-lg border text-sm mb-2 bg-yellow-900/10 border-yellow-600/30">
                              <AlertCircle className="h-4 w-4 text-yellow-500 inline-block mr-2" />
                              <span className="text-yellow-400">Feedback: {deliverable.feedback}</span>
                            </div>
                          )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          {config.badge}
                          {deliverable.submissionUrl && (
                            <Button size="sm" variant="outline" asChild>
                              <a href={deliverable.submissionUrl} target="_blank" rel="noopener noreferrer">
                                <Eye className="h-4 w-4 mr-2" />
                                View Submission
                              </a>
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })
            ) : (
              <div className="text-center py-12">
                <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-400 mb-2">No deliverables found</h3>
                <p className="text-gray-500">No deliverables for this campaign yet.</p>
              </div>
            )}
          </div>

          {/* Submit Deliverable Modal */}
          {showSubmitModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 w-full max-w-lg">
                <h2 className="text-2xl font-bold mb-4">Submit Deliverable</h2>
                <div className="space-y-4">
                  <Input
                    placeholder="Title"
                    value={submissionData.title}
                    onChange={e => setSubmissionData({ ...submissionData, title: e.target.value })}
                  />
                  <Input
                    placeholder="Description"
                    value={submissionData.description}
                    onChange={e => setSubmissionData({ ...submissionData, description: e.target.value })}
                  />
                  <Input
                    placeholder="Content URL (e.g. TikTok, YouTube, Google Drive, etc.)"
                    value={submissionData.content_url}
                    onChange={e => setSubmissionData({ ...submissionData, content_url: e.target.value })}
                  />
                  <Input
                    placeholder="Content Type (e.g. video, image, document)"
                    value={submissionData.content_type}
                    onChange={e => setSubmissionData({ ...submissionData, content_type: e.target.value })}
                  />
                  <Input
                    placeholder="Hashtags (comma separated)"
                    value={submissionData.hashtags}
                    onChange={e => setSubmissionData({ ...submissionData, hashtags: e.target.value })}
                  />
                </div>
                <div className="flex justify-end gap-2 mt-6">
                  <Button variant="outline" onClick={() => setShowSubmitModal(false)} disabled={submitting}>
                    Cancel
                  </Button>
                  <Button className="bg-purple-600 hover:bg-purple-700" onClick={handleSubmitDeliverable} disabled={submitting}>
                    {submitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Submitting...
                      </>
                    ) : (
                      "Submit"
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
} 