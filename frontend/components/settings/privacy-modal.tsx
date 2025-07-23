"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertTriangle, Shield, Eye, MessageSquare } from "lucide-react"

interface PrivacyModalProps {
  isOpen: boolean
  onClose: () => void
}

export function PrivacyModal({ isOpen, onClose }: PrivacyModalProps) {
  const [privacySettings, setPrivacySettings] = useState({
    profile: {
      publicProfile: true,
      showPerformanceStats: true,
      displayEarnings: false,
      showBadgeCollection: true,
    },
    dataSharing: {
      shareWithAgencies: true,
      allowPerformanceAnalytics: true,
      includeInPlatformStats: true,
      marketingCommunications: false,
    },
    safety: {
      blockInappropriateContent: true,
      contentFilterLevel: "moderate",
    },
    communication: {
      allowAgencyMessages: true,
      acceptCreatorMessages: true,
      showOnlineStatus: false,
    },
  })

  const updateSetting = (category: string, key: string, value: any) => {
    setPrivacySettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value,
      },
    }))
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Privacy & Safety</DialogTitle>
          <DialogDescription className="text-gray-400">
            Control your privacy settings and manage what information you share.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Profile Visibility */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Eye className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Profile Visibility</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Public profile</Label>
                  <p className="text-sm text-gray-400">Allow others to view your creator profile</p>
                </div>
                <Switch
                  checked={privacySettings.profile.publicProfile}
                  onCheckedChange={(checked) => updateSetting("profile", "publicProfile", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Show performance stats</Label>
                  <p className="text-sm text-gray-400">Display your campaign performance metrics publicly</p>
                </div>
                <Switch
                  checked={privacySettings.profile.showPerformanceStats}
                  onCheckedChange={(checked) => updateSetting("profile", "showPerformanceStats", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Display earnings publicly</Label>
                  <p className="text-sm text-gray-400">Show your earnings information on your profile</p>
                </div>
                <Switch
                  checked={privacySettings.profile.displayEarnings}
                  onCheckedChange={(checked) => updateSetting("profile", "displayEarnings", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Show badge collection</Label>
                  <p className="text-sm text-gray-400">Display your earned badges and achievements</p>
                </div>
                <Switch
                  checked={privacySettings.profile.showBadgeCollection}
                  onCheckedChange={(checked) => updateSetting("profile", "showBadgeCollection", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Data Sharing */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Shield className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Data Sharing</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Share data with agencies</Label>
                  <p className="text-sm text-gray-400">
                    Allow agencies to access your performance data for campaign matching
                  </p>
                </div>
                <Switch
                  checked={privacySettings.dataSharing.shareWithAgencies}
                  onCheckedChange={(checked) => updateSetting("dataSharing", "shareWithAgencies", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Allow performance analytics</Label>
                  <p className="text-sm text-gray-400">Enable detailed analytics tracking and reporting</p>
                </div>
                <Switch
                  checked={privacySettings.dataSharing.allowPerformanceAnalytics}
                  onCheckedChange={(checked) => updateSetting("dataSharing", "allowPerformanceAnalytics", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Include in platform statistics</Label>
                  <p className="text-sm text-gray-400">Allow your data to be used in aggregate platform statistics</p>
                </div>
                <Switch
                  checked={privacySettings.dataSharing.includeInPlatformStats}
                  onCheckedChange={(checked) => updateSetting("dataSharing", "includeInPlatformStats", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Marketing communications</Label>
                  <p className="text-sm text-gray-400">Receive promotional emails and marketing materials</p>
                </div>
                <Switch
                  checked={privacySettings.dataSharing.marketingCommunications}
                  onCheckedChange={(checked) => updateSetting("dataSharing", "marketingCommunications", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Safety Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Safety Settings</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Block inappropriate content</Label>
                  <p className="text-sm text-gray-400">Automatically filter out inappropriate or harmful content</p>
                </div>
                <Switch
                  checked={privacySettings.safety.blockInappropriateContent}
                  onCheckedChange={(checked) => updateSetting("safety", "blockInappropriateContent", checked)}
                />
              </div>

              <div>
                <Label className="text-white font-medium mb-2 block">Content filtering level</Label>
                <Select
                  value={privacySettings.safety.contentFilterLevel}
                  onValueChange={(value) => updateSetting("safety", "contentFilterLevel", value)}
                >
                  <SelectTrigger className="w-48 bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="off">Off</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="strict">Strict</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-gray-400 mt-1">
                  {privacySettings.safety.contentFilterLevel === "off" && "No content filtering applied"}
                  {privacySettings.safety.contentFilterLevel === "moderate" && "Filter obvious inappropriate content"}
                  {privacySettings.safety.contentFilterLevel === "strict" && "Strict filtering with maximum protection"}
                </p>
              </div>

              <div className="p-4 bg-gray-800 rounded-lg">
                <h4 className="text-white font-medium mb-2">Report harmful behavior</h4>
                <p className="text-sm text-gray-400 mb-3">
                  If you encounter harassment, inappropriate content, or other harmful behavior, you can report it to
                  our moderation team.
                </p>
                <Button
                  variant="outline"
                  className="border-red-600 text-red-400 hover:bg-red-600 hover:text-white bg-transparent"
                >
                  Report Content or User
                </Button>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Communication Privacy */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Communication Privacy</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Allow direct messages from agencies</Label>
                  <p className="text-sm text-gray-400">Let agencies contact you directly for campaign opportunities</p>
                </div>
                <Switch
                  checked={privacySettings.communication.allowAgencyMessages}
                  onCheckedChange={(checked) => updateSetting("communication", "allowAgencyMessages", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Accept messages from other creators</Label>
                  <p className="text-sm text-gray-400">Allow other creators to send you direct messages</p>
                </div>
                <Switch
                  checked={privacySettings.communication.acceptCreatorMessages}
                  onCheckedChange={(checked) => updateSetting("communication", "acceptCreatorMessages", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Show online status</Label>
                  <p className="text-sm text-gray-400">Display when you're active on the platform</p>
                </div>
                <Switch
                  checked={privacySettings.communication.showOnlineStatus}
                  onCheckedChange={(checked) => updateSetting("communication", "showOnlineStatus", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Privacy Information */}
          <div className="p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
            <h4 className="text-white font-medium mb-2">Your Privacy Rights</h4>
            <p className="text-sm text-gray-300 mb-3">
              You have the right to access, update, or delete your personal data at any time. We are committed to
              protecting your privacy and will never sell your personal information to third parties.
            </p>
            <div className="flex gap-3">
              <Button variant="outline" size="sm" className="border-blue-600 text-blue-400 bg-transparent">
                View Privacy Policy
              </Button>
              <Button variant="outline" size="sm" className="border-blue-600 text-blue-400 bg-transparent">
                Download My Data
              </Button>
              <Button variant="outline" size="sm" className="border-red-600 text-red-400 bg-transparent">
                Delete Account
              </Button>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Cancel
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Privacy Settings</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
