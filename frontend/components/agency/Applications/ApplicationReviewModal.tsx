import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { Check, X, Copy, MapPin, Mail, Phone, Calendar, TrendingUp, Users, Loader2 } from "lucide-react"
import { useState } from "react"
import type { Application } from "@/hooks/useApplications"

interface ApplicationReviewModalProps {
  application: Application | null
  isOpen: boolean
  onClose: () => void
  onApprove: (id: string) => Promise<void>
  onReject: (id: string) => Promise<void>
  reviewMutation: any
  formatNumber: (num: number) => string
  formatCurrency: (amount: number) => string
  getStatusColor: (status: string) => string
  getStatusIcon: (status: string) => JSX.Element
  copyToClipboard: (text: string) => void
}

export function ApplicationReviewModal({
  application,
  isOpen,
  onClose,
  onApprove,
  onReject,
  reviewMutation,
  formatNumber,
  formatCurrency,
  getStatusColor,
  getStatusIcon,
  copyToClipboard
}: ApplicationReviewModalProps) {
  const [rejectionReason, setRejectionReason] = useState("")

  if (!application) return null

  const creator = application.creator
  const campaign = application.campaign

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-xl">
            Application Review
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Review and approve or reject this creator application
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Creator Info */}
          <div className="flex items-start gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={creator?.avatar || "/placeholder.svg"} />
              <AvatarFallback className="bg-gray-800 text-white text-lg">
                {(creator?.first_name?.[0] || '') + (creator?.last_name?.[0] || '')}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-white">
                {creator?.first_name} {creator?.last_name}
              </h3>
              <p className="text-gray-400">@{creator?.username}</p>
              <div className="flex items-center gap-4 mt-2">
                <Badge className={getStatusColor(application.status)}>
                  {getStatusIcon(application.status)}
                  <span className="ml-1 capitalize">{application.status}</span>
                </Badge>
                {creator?.profile_completion && (
                  <span className="text-sm text-gray-400">
                    Profile {creator.profile_completion}% complete
                  </span>
                )}
              </div>
            </div>
          </div>

          <Separator className="bg-gray-800" />

          {/* Campaign Info */}
          <div>
            <h4 className="text-lg font-medium text-white mb-2">Campaign</h4>
            <div className="bg-gray-800 p-4 rounded-lg">
              <h5 className="font-medium text-purple-400">{campaign?.name}</h5>
              <p className="text-sm text-gray-400 mt-1">{campaign?.description}</p>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-sm text-gray-400">
                  Applied: {new Date(application.applied_at).toLocaleDateString()}
                </span>
                <span className="text-sm text-gray-400">
                  Campaign Status: {campaign?.status}
                </span>
              </div>
            </div>
          </div>

          {/* Application Message */}
          {application.application_message && (
            <div>
              <h4 className="text-lg font-medium text-white mb-2">Application Message</h4>
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-gray-300">{application.application_message}</p>
              </div>
            </div>
          )}

          <Separator className="bg-gray-800" />

          {/* Creator Metrics */}
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Creator Metrics</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="h-5 w-5 text-green-400" />
                  <span className="font-medium text-white">Performance</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Previous GMV:</span>
                    <span className="text-green-400 font-semibold">
                      {application.previous_gmv ? formatCurrency(application.previous_gmv) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Engagement Rate:</span>
                    <span className="text-white">
                      {application.engagement_rate ? `${application.engagement_rate}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Followers:</span>
                    <span className="text-white">
                      {creator?.total_followers ? formatNumber(creator.total_followers) : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="h-5 w-5 text-purple-400" />
                  <span className="font-medium text-white">Social Platforms</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">TikTok:</span>
                    <span className="text-white">
                      {creator?.tiktok_handle || 'N/A'}
                      {creator?.tiktok_followers && ` (${formatNumber(creator.tiktok_followers)})`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Instagram:</span>
                    <span className="text-white">
                      {creator?.instagram_handle || 'N/A'}
                      {creator?.instagram_followers && ` (${formatNumber(creator.instagram_followers)})`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">YouTube:</span>
                    <span className="text-white">
                      {creator?.youtube_handle || 'N/A'}
                      {creator?.youtube_followers && ` (${formatNumber(creator.youtube_followers)})`}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Demographics */}
          {(creator?.audience_gender || creator?.primary_age || creator?.location) && (
            <div>
              <h4 className="text-lg font-medium text-white mb-4">Demographics</h4>
              <div className="bg-gray-800 p-4 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  {creator?.audience_gender && (
                    <div>
                      <span className="text-gray-400">Audience Gender:</span>
                      <div className="mt-1">
                        <span className="text-blue-400">Male: {creator.audience_gender.male}%</span>
                        <span className="text-pink-400 ml-4">Female: {creator.audience_gender.female}%</span>
                      </div>
                    </div>
                  )}
                  {creator?.primary_age && (
                    <div>
                      <span className="text-gray-400">Primary Age:</span>
                      <div className="text-white mt-1">{creator.primary_age}</div>
                    </div>
                  )}
                  {creator?.location && (
                    <div>
                      <span className="text-gray-400">Location:</span>
                      <div className="text-white mt-1">{creator.location}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Contact Info */}
          <div>
            <h4 className="text-lg font-medium text-white mb-4">Contact Information</h4>
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                {creator?.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <span className="text-white">{creator.email}</span>
                                         <Button
                       size="sm"
                       variant="ghost"
                       className="h-6 w-6 p-0"
                       onClick={() => copyToClipboard(creator.email || '')}
                     >
                       <Copy className="h-3 w-3" />
                     </Button>
                  </div>
                )}
                {creator?.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <span className="text-white">{creator.phone}</span>
                                         <Button
                       size="sm"
                       variant="ghost"
                       className="h-6 w-6 p-0"
                       onClick={() => copyToClipboard(creator.phone || '')}
                     >
                       <Copy className="h-3 w-3" />
                     </Button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {application.status === "pending" && (
            <div className="space-y-4">
              <Separator className="bg-gray-800" />
              <div>
                <h4 className="text-lg font-medium text-white mb-2">Review Decision</h4>
                <div className="space-y-3">
                  <Textarea
                    placeholder="Add review notes or rejection reason (optional)..."
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    className="bg-gray-800 border-gray-700 text-white"
                  />
                  <div className="flex gap-3">
                    <Button
                      className="bg-green-600 hover:bg-green-700 flex-1"
                      onClick={() => onApprove(application.id)}
                      disabled={reviewMutation.isPending}
                    >
                      {reviewMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <Check className="h-4 w-4 mr-2" />
                      )}
                      Approve Application
                    </Button>
                    <Button
                      variant="destructive"
                      className="flex-1"
                      onClick={() => onReject(application.id)}
                      disabled={reviewMutation.isPending}
                    >
                      {reviewMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (
                        <X className="h-4 w-4 mr-2" />
                      )}
                      Reject Application
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end pt-4">
            <Button variant="outline" onClick={onClose} className="border-gray-700 hover:bg-gray-800">
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 