"use client"

import { useState } from "react"
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
  Upload,
  Video,
  Image,
  FileText,
  Eye,
  Download,
  Trash2,
  Edit,
  Play,
  Calendar,
  Tag,
  Filter,
  Plus,
  AlertTriangle,
  RefreshCw,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/hooks/useAuth"
import { useContent, type ContentItem } from "@/hooks/useContent"
import { toast } from "@/components/ui/use-toast"

export default function CreatorContentPage() {
  const { user, isAuthenticated } = useAuth()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  
  // Get content data from the hook
  const { content, loading, error, refetch, uploadFile, deleteContent } = useContent()

  const filteredContent = content.filter(item => {
    const matchesSearch = 
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
      item.campaign?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === "all" || item.type === typeFilter
    const matchesStatus = statusFilter === "all" || item.status === statusFilter

    return matchesSearch && matchesType && matchesStatus
  })

  const getTypeIcon = (type: ContentItem["type"]) => {
    switch (type) {
      case "video":
        return <Video className="h-5 w-5 text-red-400" />
      case "image":
        return <Image className="h-5 w-5 text-green-400" />
      case "document":
        return <FileText className="h-5 w-5 text-blue-400" />
      default:
        return <FileText className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusBadge = (status: ContentItem["status"]) => {
    switch (status) {
      case "approved":
        return <Badge className="bg-green-600 hover:bg-green-700">Approved</Badge>
      case "pending":
        return <Badge className="bg-yellow-600 hover:bg-yellow-700">Pending</Badge>
      case "rejected":
        return <Badge className="bg-red-600 hover:bg-red-700">Rejected</Badge>
      case "draft":
        return <Badge className="bg-gray-600 hover:bg-gray-700">Draft</Badge>
      default:
        return <Badge className="bg-gray-600 hover:bg-gray-700">{status}</Badge>
    }
  }

  // Calculate stats
  const stats = {
    total: filteredContent.length,
    videos: filteredContent.filter(item => item.type === 'video').length,
    images: filteredContent.filter(item => item.type === 'image').length,
    documents: filteredContent.filter(item => item.type === 'document').length,
    totalViews: filteredContent.reduce((sum, item) => sum + (item.views || 0), 0),
  }

  const handleRetry = () => {
    refetch()
    toast({
      title: "Refreshing",
      description: "Fetching latest content...",
    })
  }

  const handleDelete = async (item: ContentItem) => {
    if (window.confirm(`Are you sure you want to delete "${item.name}"?`)) {
      const result = await deleteContent(item.id, item.source)
      if (result.success) {
        toast({
          title: "Content Deleted",
          description: "The content has been successfully deleted.",
        })
      } else {
        toast({
          title: "Delete Failed",
          description: result.error || "Failed to delete content.",
          variant: "destructive"
        })
      }
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const file = files[0]
    const result = await uploadFile(file, { folder: 'content-library' })
    
    if (result.success) {
      toast({
        title: "Upload Successful",
        description: "Your file has been uploaded successfully.",
      })
    } else {
      toast({
        title: "Upload Failed",
        description: result.error || "Failed to upload file.",
        variant: "destructive"
      })
    }

    // Reset the input
    event.target.value = ''
  }

  const renderGridView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredContent.map((item) => (
        <Card key={item.id} className="bg-gray-900 border-gray-800 hover:border-purple-500/50 transition-all duration-300">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getTypeIcon(item.type)}
                <span className="text-sm font-medium capitalize">{item.type}</span>
                <Badge variant="outline" className="text-xs">
                  {item.source}
                </Badge>
              </div>
              {getStatusBadge(item.status)}
            </div>
            
            {/* Thumbnail/Preview */}
            <div className="aspect-video bg-gray-800 rounded-lg overflow-hidden relative">
              {item.thumbnail ? (
                <img src={item.thumbnail} alt={item.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  {getTypeIcon(item.type)}
                </div>
              )}
              {item.type === "video" && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="bg-black/50 rounded-full p-2">
                    <Play className="h-6 w-6 text-white" />
                  </div>
                </div>
              )}
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold text-lg mb-1">{item.name}</h3>
              {item.campaign && (
                <p className="text-gray-400 text-sm">{item.campaign}</p>
              )}
            </div>

            <div className="flex flex-wrap gap-1">
              {item.tags.map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>

            <div className="flex items-center justify-between text-sm text-gray-400">
              <span>{item.size}</span>
              <span>{new Date(item.uploadDate).toLocaleDateString()}</span>
            </div>

            {item.views && (
              <div className="flex items-center gap-2 text-sm text-purple-400">
                <Eye className="h-4 w-4" />
                <span>{item.views.toLocaleString()} views</span>
              </div>
            )}

            <div className="flex gap-2">
              <Button size="sm" variant="outline" className="flex-1" asChild>
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  <Eye className="h-4 w-4 mr-2" />
                  View
                </a>
              </Button>
              <Button size="sm" variant="outline" asChild>
                <a href={item.url} download>
                  <Download className="h-4 w-4" />
                </a>
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => handleDelete(item)}
                className="text-red-400 hover:text-red-300"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )

  const renderListView = () => (
    <div className="space-y-4">
      {filteredContent.map((item) => (
        <Card key={item.id} className="bg-gray-900 border-gray-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-gray-800 rounded-lg flex items-center justify-center">
                  {getTypeIcon(item.type)}
                </div>
                <div>
                  <h3 className="font-semibold">{item.name}</h3>
                  <p className="text-sm text-gray-400">{item.campaign}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500 mt-1">
                    <span>{item.size}</span>
                    <span>{new Date(item.uploadDate).toLocaleDateString()}</span>
                    {item.views && <span>{item.views.toLocaleString()} views</span>}
                    <Badge variant="outline" className="text-xs">
                      {item.source}
                    </Badge>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {getStatusBadge(item.status)}
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" asChild>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      <Eye className="h-4 w-4" />
                    </a>
                  </Button>
                  <Button size="sm" variant="outline" asChild>
                    <a href={item.url} download>
                      <Download className="h-4 w-4" />
                    </a>
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={() => handleDelete(item)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )

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
                <p className="text-gray-400">Loading your content...</p>
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
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">Content Library</h1>
                <p className="text-gray-400 text-lg">Manage your uploaded content and submitted deliverables</p>
              </div>
              <div className="flex gap-2">
                <Button className="bg-purple-600 hover:bg-purple-700" onClick={() => document.getElementById('file-upload')?.click()}>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Content
                </Button>
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept="image/*,video/*,.pdf,.doc,.docx"
                  onChange={handleFileUpload}
                />
              </div>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 bg-red-900/20 border border-red-600/30 rounded-lg p-4 flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-red-500 font-medium">Error Loading Content</p>
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
                <CardTitle className="text-sm font-medium text-gray-400">Total Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
                <p className="text-xs text-gray-400 mt-1">All content</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Videos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-400">{stats.videos}</div>
                <p className="text-xs text-gray-400 mt-1">Video files</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Images</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-400">{stats.images}</div>
                <p className="text-xs text-gray-400 mt-1">Image files</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Total Views</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-400">{stats.totalViews.toLocaleString()}</div>
                <p className="text-xs text-gray-400 mt-1">Content views</p>
              </CardContent>
            </Card>
          </div>

          {/* Filters and Controls */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-gray-900 border-gray-800"
              />
            </div>
            
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[120px] bg-gray-900 border-gray-800">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-800">
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="video">Videos</SelectItem>
                <SelectItem value="image">Images</SelectItem>
                <SelectItem value="document">Documents</SelectItem>
              </SelectContent>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[120px] bg-gray-900 border-gray-800">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent className="bg-gray-900 border-gray-800">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex border border-gray-800 rounded-lg">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="rounded-r-none"
              >
                Grid
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="rounded-l-none"
              >
                List
              </Button>
            </div>
          </div>

          {/* Content Grid/List */}
          <Tabs defaultValue="all" className="space-y-6">
            <TabsList className="bg-gray-900 border-gray-800">
              <TabsTrigger value="all" className="data-[state=active]:bg-purple-600">
                All Content
              </TabsTrigger>
              <TabsTrigger value="videos" className="data-[state=active]:bg-purple-600">
                Videos ({stats.videos})
              </TabsTrigger>
              <TabsTrigger value="images" className="data-[state=active]:bg-purple-600">
                Images ({stats.images})
              </TabsTrigger>
              <TabsTrigger value="documents" className="data-[state=active]:bg-purple-600">
                Documents ({stats.documents})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="all">
              {filteredContent.length > 0 ? (
                viewMode === "grid" ? renderGridView() : renderListView()
              ) : (
                <div className="text-center py-12">
                  <Upload className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No content found</h3>
                  <p className="text-gray-500 mb-4">
                    {searchQuery ? "Try adjusting your search or filters" : "Upload your first content or submit deliverables to get started"}
                  </p>
                  <Button 
                    className="bg-purple-600 hover:bg-purple-700"
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Content
                  </Button>
                </div>
              )}
            </TabsContent>

            <TabsContent value="videos">
              {filteredContent.filter(item => item.type === 'video').length > 0 ? (
                viewMode === "grid" ? renderGridView() : renderListView()
              ) : (
                <div className="text-center py-12">
                  <Video className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No videos found</h3>
                  <p className="text-gray-500">Upload video content to see them here</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="images">
              {filteredContent.filter(item => item.type === 'image').length > 0 ? (
                viewMode === "grid" ? renderGridView() : renderListView()
              ) : (
                <div className="text-center py-12">
                  <Image className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No images found</h3>
                  <p className="text-gray-500">Upload image content to see them here</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="documents">
              {filteredContent.filter(item => item.type === 'document').length > 0 ? (
                viewMode === "grid" ? renderGridView() : renderListView()
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No documents found</h3>
                  <p className="text-gray-500">Upload document content to see them here</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
} 