"use client"

import {
  Search,
  Download,
  UserPlus,
  Settings,
  Calendar,
  Eye,
  MessageSquare,
  Check,
  X,
  Copy,
  Star,
  TrendingUp,
  Users,
  Clock,
  Mail,
  Phone,
  MapPin,
  BarChart3,
  Send,
  Home,
  ChevronRight,
  SlidersHorizontal,
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { AgencySidebar } from "@/components/agency/navigation/agency-sidebar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

// Import the custom hook
import { useCreatorApplications } from "@/hooks/useCreatorApplications"

// Components
import { ApplicationsHeader } from "@/components/agency/Applications/ApplicationsHeader"
import { ApplicationsStats } from "@/components/agency/Applications/ApplicationsStats"
import { ApplicationsFilters } from "@/components/agency/Applications/ApplicationsFilters"
import { ApplicationsTable } from "@/components/agency/Applications/ApplicationsTable"
import { ApplicationReviewModal } from "@/components/agency/Applications/ApplicationReviewModal"

const statusOptions = ["All", "pending", "approved", "rejected"]

export default function CreatorApplications() {
  const {
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
  } = useCreatorApplications()

  // Loading state
  if (campaignsLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="flex items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading campaigns...</span>
        </div>
      </div>
    )
  }

  // Error state
  if (applicationsError) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Error Loading Applications</h2>
          <p className="text-gray-400 mb-4">
            {applicationsError.message || "Failed to load applications. Please try again."}
          </p>
          <Button onClick={() => window.location.reload()} className="bg-purple-600 hover:bg-purple-700">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <AgencySidebar />
      
      <div className="flex-1 lg:ml-60">
        {/* Header */}
        <div className="border-b border-gray-800 bg-black/50 backdrop-blur-sm sticky top-0 z-40">
          <div className="px-6 py-4">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
              <Home className="h-4 w-4" />
              <ChevronRight className="h-4 w-4" />
              <span>Creators</span>
              <ChevronRight className="h-4 w-4" />
              <span className="text-purple-400">Applications</span>
            </div>

            <ApplicationsHeader
              applicationsCount={filteredApplications.length}
              isLoading={applicationsLoading}
              onInviteClick={() => setShowInviteModal(true)}
            />

            <ApplicationsStats
              totalApplications={totalApplications}
              pendingApplications={pendingApplications}
              approvalRate={approvalRate}
              isLoading={applicationsLoading}
            />

            <ApplicationsFilters
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              statusFilter={statusFilter}
              onStatusChange={setStatusFilter}
              selectedCampaignId={selectedCampaignId}
              onCampaignChange={(value: string) => {
                setSelectedCampaignId(value)
                setCampaignFilter(campaigns.find(c => c.id === value)?.name || "All Campaigns")
              }}
              campaigns={campaigns}
              dateRange={dateRange}
              onDateRangeChange={setDateRange}
              showFilters={showFilters}
              onShowFiltersChange={setShowFilters}
              statusOptions={statusOptions}
            />

            {/* Bulk Actions */}
            {selectedApplications.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-400">
                      {selectedApplications.length} applications selected
                    </span>
                    <Button
                      size="sm"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={handleBulkApprove}
                      disabled={bulkReviewMutation.isPending}
                    >
                      {bulkReviewMutation.isPending ? (
                        <Loader2 className="h-3 w-3 animate-spin mr-1" />
                      ) : (
                        <Check className="h-3 w-3 mr-1" />
                      )}
                      Approve All
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={handleBulkReject}
                      disabled={bulkReviewMutation.isPending}
                    >
                      {bulkReviewMutation.isPending ? (
                        <Loader2 className="h-3 w-3 animate-spin mr-1" />
                      ) : (
                        <X className="h-3 w-3 mr-1" />
                      )}
                      Reject All
                    </Button>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setSelectedApplications([])}
                    className="text-gray-400 hover:text-white"
                  >
                    Clear Selection
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Applications Table */}
        <div className="p-6">
          <ApplicationsTable
            applications={filteredApplications}
            selectedApplications={selectedApplications}
            onSelectAll={handleSelectAll}
            onSelectApplication={handleSelectApplication}
            onApprove={handleApproveApplication}
            onReject={handleRejectApplication}
            onViewDetails={setSelectedApplication}
            isLoading={applicationsLoading}
            reviewMutation={reviewMutation}
            formatNumber={formatNumber}
            formatCurrency={formatCurrency}
            getStatusColor={getStatusColor}
          />
        </div>

        {/* Modals */}
        <ApplicationReviewModal
          application={selectedApplication}
          isOpen={!!selectedApplication}
          onClose={() => setSelectedApplication(null)}
          onApprove={handleApproveApplication}
          onReject={handleRejectApplication}
          reviewMutation={reviewMutation}
          formatNumber={formatNumber}
          formatCurrency={formatCurrency}
          getStatusColor={getStatusColor}
          getStatusIcon={(status: string) => {
            // Convert string to actual icon component
            if (status === "approved") return <Check className="h-3 w-3 text-green-400" />
            if (status === "rejected") return <X className="h-3 w-3 text-red-400" />
            if (status === "pending") return <Clock className="h-3 w-3 text-yellow-400" />
            return <AlertCircle className="h-3 w-3 text-gray-400" />
          }}
          copyToClipboard={copyToClipboard}
        />

        {/* Simple Invite Modal */}
        {showInviteModal && (
          <Dialog open={showInviteModal} onOpenChange={setShowInviteModal}>
            <DialogContent className="bg-gray-900 border-gray-800">
              <DialogHeader>
                <DialogTitle className="text-white">Invite Creators</DialogTitle>
                <DialogDescription className="text-gray-400">
                  Feature coming soon. Creator invitation functionality will be available in the next update.
                </DialogDescription>
              </DialogHeader>
              <div className="flex justify-end pt-4">
                <Button 
                  onClick={() => setShowInviteModal(false)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  Close
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  )
}
