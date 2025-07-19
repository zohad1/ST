"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface CampaignPreferencesModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CampaignPreferencesModal({ isOpen, onClose }: CampaignPreferencesModalProps) {
  const [preferences, setPreferences] = useState({
    discovery: {
      autoApply: false,
      campaignTypes: {
        fashion: true,
        tech: true,
        beauty: true,
        lifestyle: true,
      },
      minPayout: [50],
      maxCampaigns: 5,
    },
    content: {
      types: {
        video: true,
        images: true,
        stories: true,
        lives: false,
      },
      style: ["Fashion Focus", "Product Reviews", "Lifestyle"],
      schedule: "flexible",
    },
    application: {
      autoAcceptPreApproved: false,
      requireDetails: true,
      emailConfirmation: true,
    },
    collaboration: {
      collaborateWithCreators: true,
      outsidePlatformPartnerships: false,
      urgentCampaigns: true,
    },
  })

  const updatePreference = (category: string, key: string, value: any) => {
    setPreferences((prev) => ({
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
          <DialogTitle className="text-white text-2xl">Campaign Preferences</DialogTitle>
          <DialogDescription className="text-gray-400">
            Configure your campaign discovery and application settings.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Campaign Discovery */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Campaign Discovery</h3>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Auto-apply to matching campaigns</Label>
                  <p className="text-sm text-gray-400">Automatically apply to campaigns that match your preferences</p>
                </div>
                <Switch
                  checked={preferences.discovery.autoApply}
                  onCheckedChange={(checked) => updatePreference("discovery", "autoApply", checked)}
                />
              </div>

              <div>
                <Label className="text-white font-medium mb-3 block">Preferred campaign types</Label>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(preferences.discovery.campaignTypes).map(([type, checked]) => (
                    <div key={type} className="flex items-center space-x-2">
                      <Checkbox
                        id={type}
                        checked={checked}
                        onCheckedChange={(isChecked) =>
                          updatePreference("discovery", "campaignTypes", {
                            ...preferences.discovery.campaignTypes,
                            [type]: isChecked,
                          })
                        }
                      />
                      <Label htmlFor={type} className="text-white capitalize">
                        {type}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-3 block">
                  Minimum payout threshold: ${preferences.discovery.minPayout[0]}
                </Label>
                <Slider
                  value={preferences.discovery.minPayout}
                  onValueChange={(value) => updatePreference("discovery", "minPayout", value)}
                  max={500}
                  min={25}
                  step={25}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-400 mt-1">
                  <span>$25</span>
                  <span>$500</span>
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-2 block">Maximum campaigns per month</Label>
                <Input
                  type="number"
                  value={preferences.discovery.maxCampaigns}
                  onChange={(e) => updatePreference("discovery", "maxCampaigns", Number.parseInt(e.target.value))}
                  className="w-32 bg-gray-800 border-gray-700 text-white"
                  min={1}
                  max={20}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Content Preferences */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Content Preferences</h3>
            <div className="space-y-6">
              <div>
                <Label className="text-white font-medium mb-3 block">Preferred content types</Label>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(preferences.content.types).map(([type, checked]) => (
                    <div key={type} className="flex items-center space-x-2">
                      <Checkbox
                        id={`content-${type}`}
                        checked={checked}
                        onCheckedChange={(isChecked) =>
                          updatePreference("content", "types", {
                            ...preferences.content.types,
                            [type]: isChecked,
                          })
                        }
                      />
                      <Label htmlFor={`content-${type}`} className="text-white capitalize">
                        {type}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-2 block">Content style</Label>
                <div className="flex flex-wrap gap-2">
                  {preferences.content.style.map((style, index) => (
                    <div key={index} className="bg-purple-600/20 text-purple-400 px-3 py-1 rounded-full text-sm">
                      {style}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-2 block">Posting schedule preferences</Label>
                <Select
                  value={preferences.content.schedule}
                  onValueChange={(value) => updatePreference("content", "schedule", value)}
                >
                  <SelectTrigger className="w-64 bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="flexible">Flexible</SelectItem>
                    <SelectItem value="weekdays">Weekdays only</SelectItem>
                    <SelectItem value="weekends">Weekends only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Application Settings */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Application Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Auto-accept pre-approved campaigns</Label>
                  <p className="text-sm text-gray-400">Automatically accept campaigns you're pre-approved for</p>
                </div>
                <Switch
                  checked={preferences.application.autoAcceptPreApproved}
                  onCheckedChange={(checked) => updatePreference("application", "autoAcceptPreApproved", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Require campaign details before applying</Label>
                  <p className="text-sm text-gray-400">Show full campaign details before allowing applications</p>
                </div>
                <Switch
                  checked={preferences.application.requireDetails}
                  onCheckedChange={(checked) => updatePreference("application", "requireDetails", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Email confirmation for applications</Label>
                  <p className="text-sm text-gray-400">Send email confirmation when you apply to campaigns</p>
                </div>
                <Switch
                  checked={preferences.application.emailConfirmation}
                  onCheckedChange={(checked) => updatePreference("application", "emailConfirmation", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Collaboration Preferences */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Collaboration Preferences</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Willing to collaborate with other creators</Label>
                  <p className="text-sm text-gray-400">Allow joint campaigns with other creators</p>
                </div>
                <Switch
                  checked={preferences.collaboration.collaborateWithCreators}
                  onCheckedChange={(checked) => updatePreference("collaboration", "collaborateWithCreators", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Open to brand partnerships outside platform</Label>
                  <p className="text-sm text-gray-400">Allow brands to contact you for external partnerships</p>
                </div>
                <Switch
                  checked={preferences.collaboration.outsidePlatformPartnerships}
                  onCheckedChange={(checked) =>
                    updatePreference("collaboration", "outsidePlatformPartnerships", checked)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Available for urgent campaigns</Label>
                  <p className="text-sm text-gray-400">Receive notifications for time-sensitive opportunities</p>
                </div>
                <Switch
                  checked={preferences.collaboration.urgentCampaigns}
                  onCheckedChange={(checked) => updatePreference("collaboration", "urgentCampaigns", checked)}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Cancel
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Preferences</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
