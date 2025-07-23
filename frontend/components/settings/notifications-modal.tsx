"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface NotificationsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationsModal({ isOpen, onClose }: NotificationsModalProps) {
  const [settings, setSettings] = useState({
    campaign: {
      newInvitations: { email: true, sms: true, inApp: true },
      updates: { email: true, sms: false, inApp: true },
      deadlines: { email: true, sms: true, inApp: true },
      completion: { email: true, sms: false, inApp: true },
    },
    performance: {
      gmvMilestones: { email: true, sms: true, inApp: true },
      contentAlerts: { email: true, sms: false, inApp: true },
      leaderboard: { email: false, sms: false, inApp: true },
      badges: { email: true, sms: true, inApp: true },
    },
    payment: {
      processing: { email: true, sms: true, inApp: true },
      confirmations: { email: true, sms: false, inApp: true },
      bonuses: { email: true, sms: true, inApp: true },
      issues: { email: true, sms: true, inApp: true },
    },
    communication: {
      agencyMessages: { email: false, sms: false, inApp: true },
      brandFeedback: { email: true, sms: false, inApp: true },
      contentReview: { email: true, sms: false, inApp: true },
    },
    timing: {
      quietHours: true,
      weekendNotifications: true,
      digestFrequency: "immediate",
    },
  })

  const updateSetting = (category: string, item: string, type: string, value: boolean) => {
    setSettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [item]: {
          ...(prev[category as keyof typeof prev] as any)[item],
          [type]: value,
        },
      },
    }))
  }

  const NotificationRow = ({
    title,
    category,
    item,
    settings: itemSettings,
  }: {
    title: string
    category: string
    item: string
    settings: { email: boolean; sms: boolean; inApp: boolean }
  }) => (
    <div className="flex items-center justify-between py-3">
      <Label className="text-white font-medium">{title}</Label>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Switch
            checked={itemSettings.email}
            onCheckedChange={(checked) => updateSetting(category, item, "email", checked)}
          />
          <span className="text-sm text-gray-400">Email</span>
        </div>
        <div className="flex items-center gap-2">
          <Switch
            checked={itemSettings.sms}
            onCheckedChange={(checked) => updateSetting(category, item, "sms", checked)}
          />
          <span className="text-sm text-gray-400">SMS</span>
        </div>
        <div className="flex items-center gap-2">
          <Switch
            checked={itemSettings.inApp}
            onCheckedChange={(checked) => updateSetting(category, item, "inApp", checked)}
          />
          <span className="text-sm text-gray-400">In-app</span>
        </div>
      </div>
    </div>
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Notification Settings</DialogTitle>
          <DialogDescription className="text-gray-400">
            Choose how you want to be notified about your LaunchPaid activities.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Campaign Notifications */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Campaign Notifications</h3>
            <div className="space-y-1">
              <NotificationRow
                title="New campaign invitations"
                category="campaign"
                item="newInvitations"
                settings={settings.campaign.newInvitations}
              />
              <NotificationRow
                title="Campaign updates and changes"
                category="campaign"
                item="updates"
                settings={settings.campaign.updates}
              />
              <NotificationRow
                title="Deliverable deadlines"
                category="campaign"
                item="deadlines"
                settings={settings.campaign.deadlines}
              />
              <NotificationRow
                title="Campaign completion"
                category="campaign"
                item="completion"
                settings={settings.campaign.completion}
              />
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Performance Notifications */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Performance Notifications</h3>
            <div className="space-y-1">
              <NotificationRow
                title="GMV milestones reached"
                category="performance"
                item="gmvMilestones"
                settings={settings.performance.gmvMilestones}
              />
              <NotificationRow
                title="Content performance alerts"
                category="performance"
                item="contentAlerts"
                settings={settings.performance.contentAlerts}
              />
              <NotificationRow
                title="Leaderboard position changes"
                category="performance"
                item="leaderboard"
                settings={settings.performance.leaderboard}
              />
              <NotificationRow
                title="Badge achievements"
                category="performance"
                item="badges"
                settings={settings.performance.badges}
              />
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Payment Notifications */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Payment Notifications</h3>
            <div className="space-y-1">
              <NotificationRow
                title="Payout processing"
                category="payment"
                item="processing"
                settings={settings.payment.processing}
              />
              <NotificationRow
                title="Payment confirmations"
                category="payment"
                item="confirmations"
                settings={settings.payment.confirmations}
              />
              <NotificationRow
                title="Bonus earnings"
                category="payment"
                item="bonuses"
                settings={settings.payment.bonuses}
              />
              <NotificationRow
                title="Payment issues"
                category="payment"
                item="issues"
                settings={settings.payment.issues}
              />
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Communication Notifications */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Communication Notifications</h3>
            <div className="space-y-1">
              <NotificationRow
                title="Agency messages"
                category="communication"
                item="agencyMessages"
                settings={settings.communication.agencyMessages}
              />
              <NotificationRow
                title="Brand feedback"
                category="communication"
                item="brandFeedback"
                settings={settings.communication.brandFeedback}
              />
              <NotificationRow
                title="Content review results"
                category="communication"
                item="contentReview"
                settings={settings.communication.contentReview}
              />
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Notification Timing */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Notification Timing</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Quiet hours</Label>
                  <p className="text-sm text-gray-400">10 PM - 8 AM</p>
                </div>
                <Switch
                  checked={settings.timing.quietHours}
                  onCheckedChange={(checked) =>
                    setSettings((prev) => ({
                      ...prev,
                      timing: { ...prev.timing, quietHours: checked },
                    }))
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-white font-medium">Weekend notifications</Label>
                <Switch
                  checked={settings.timing.weekendNotifications}
                  onCheckedChange={(checked) =>
                    setSettings((prev) => ({
                      ...prev,
                      timing: { ...prev.timing, weekendNotifications: checked },
                    }))
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-white font-medium">Digest frequency</Label>
                <Select
                  value={settings.timing.digestFrequency}
                  onValueChange={(value) =>
                    setSettings((prev) => ({
                      ...prev,
                      timing: { ...prev.timing, digestFrequency: value },
                    }))
                  }
                >
                  <SelectTrigger className="w-40 bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="immediate">Immediate</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Cancel
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Changes</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
