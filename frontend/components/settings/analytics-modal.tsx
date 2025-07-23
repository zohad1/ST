"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"

interface AnalyticsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AnalyticsModal({ isOpen, onClose }: AnalyticsModalProps) {
  const [settings, setSettings] = useState({
    tracking: {
      gmvAttribution: true,
      engagementAnalytics: true,
      audienceGrowth: true,
      conversionRates: true,
    },
    visibility: {
      shareWithAgencies: true,
      allowComparisons: true,
      includeInLeaderboards: true,
      showToOtherCreators: false,
    },
    frequency: {
      realTimeUpdates: true,
      dailyEmails: false,
      weeklySummary: true,
      monthlyDeepDive: true,
    },
    customMetrics: {
      focusMetrics: ["GMV", "Engagement", "Reach", "Conversions"],
      monthlyGmvTarget: 5000,
      postFrequencyGoal: 12,
      benchmarkComparisons: ["network-average", "top-performers"],
    },
  })

  const updateSetting = (category: string, key: string, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value,
      },
    }))
  }

  const focusMetricOptions = ["GMV", "Engagement", "Reach", "Conversions", "Click-through Rate", "Audience Growth"]
  const benchmarkOptions = [
    { id: "network-average", label: "Against network average" },
    { id: "top-performers", label: "Against top performers" },
    { id: "similar-creators", label: "Against similar creators" },
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Performance & Analytics</DialogTitle>
          <DialogDescription className="text-gray-400">
            Configure how your performance data is tracked and displayed.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Performance Tracking */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Performance Tracking</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Track GMV attribution</Label>
                  <p className="text-sm text-gray-400">Monitor revenue generated from your content</p>
                </div>
                <Switch
                  checked={settings.tracking.gmvAttribution}
                  onCheckedChange={(checked) => updateSetting("tracking", "gmvAttribution", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Include engagement analytics</Label>
                  <p className="text-sm text-gray-400">Track likes, comments, shares, and saves</p>
                </div>
                <Switch
                  checked={settings.tracking.engagementAnalytics}
                  onCheckedChange={(checked) => updateSetting("tracking", "engagementAnalytics", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Monitor audience growth</Label>
                  <p className="text-sm text-gray-400">Track follower growth and audience insights</p>
                </div>
                <Switch
                  checked={settings.tracking.audienceGrowth}
                  onCheckedChange={(checked) => updateSetting("tracking", "audienceGrowth", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Track conversion rates</Label>
                  <p className="text-sm text-gray-400">Monitor how your content drives purchases</p>
                </div>
                <Switch
                  checked={settings.tracking.conversionRates}
                  onCheckedChange={(checked) => updateSetting("tracking", "conversionRates", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Data Visibility */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Data Visibility</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Share performance with agencies</Label>
                  <p className="text-sm text-gray-400">Allow agencies to view your performance metrics</p>
                </div>
                <Switch
                  checked={settings.visibility.shareWithAgencies}
                  onCheckedChange={(checked) => updateSetting("visibility", "shareWithAgencies", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Allow performance comparisons</Label>
                  <p className="text-sm text-gray-400">Enable benchmarking against other creators</p>
                </div>
                <Switch
                  checked={settings.visibility.allowComparisons}
                  onCheckedChange={(checked) => updateSetting("visibility", "allowComparisons", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Include in leaderboards</Label>
                  <p className="text-sm text-gray-400">Show your performance on public leaderboards</p>
                </div>
                <Switch
                  checked={settings.visibility.includeInLeaderboards}
                  onCheckedChange={(checked) => updateSetting("visibility", "includeInLeaderboards", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Show performance to other creators</Label>
                  <p className="text-sm text-gray-400">Allow other creators to see your metrics</p>
                </div>
                <Switch
                  checked={settings.visibility.showToOtherCreators}
                  onCheckedChange={(checked) => updateSetting("visibility", "showToOtherCreators", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Analytics Frequency */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Analytics Frequency</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Real-time updates</Label>
                  <p className="text-sm text-gray-400">Get instant notifications for performance changes</p>
                </div>
                <Switch
                  checked={settings.frequency.realTimeUpdates}
                  onCheckedChange={(checked) => updateSetting("frequency", "realTimeUpdates", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Daily performance emails</Label>
                  <p className="text-sm text-gray-400">Receive daily performance summaries via email</p>
                </div>
                <Switch
                  checked={settings.frequency.dailyEmails}
                  onCheckedChange={(checked) => updateSetting("frequency", "dailyEmails", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Weekly summary reports</Label>
                  <p className="text-sm text-gray-400">Get comprehensive weekly performance reports</p>
                </div>
                <Switch
                  checked={settings.frequency.weeklySummary}
                  onCheckedChange={(checked) => updateSetting("frequency", "weeklySummary", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Monthly analytics deep dive</Label>
                  <p className="text-sm text-gray-400">Detailed monthly analysis with insights and recommendations</p>
                </div>
                <Switch
                  checked={settings.frequency.monthlyDeepDive}
                  onCheckedChange={(checked) => updateSetting("frequency", "monthlyDeepDive", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Custom Metrics */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Custom Metrics</h3>
            <div className="space-y-6">
              <div>
                <Label className="text-white font-medium mb-3 block">Focus metrics</Label>
                <div className="grid grid-cols-2 gap-3">
                  {focusMetricOptions.map((metric) => (
                    <div key={metric} className="flex items-center space-x-2">
                      <Checkbox
                        id={`metric-${metric}`}
                        checked={settings.customMetrics.focusMetrics.includes(metric)}
                        onCheckedChange={(checked) => {
                          const currentMetrics = settings.customMetrics.focusMetrics
                          const updatedMetrics = checked
                            ? [...currentMetrics, metric]
                            : currentMetrics.filter((m) => m !== metric)
                          updateSetting("customMetrics", "focusMetrics", updatedMetrics)
                        }}
                      />
                      <Label htmlFor={`metric-${metric}`} className="text-white text-sm">
                        {metric}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label className="text-white font-medium mb-2 block">Monthly GMV target</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">$</span>
                    <Input
                      type="number"
                      value={settings.customMetrics.monthlyGmvTarget}
                      onChange={(e) =>
                        updateSetting("customMetrics", "monthlyGmvTarget", Number.parseInt(e.target.value))
                      }
                      className="bg-gray-800 border-gray-700 text-white"
                      min={0}
                    />
                  </div>
                </div>
                <div>
                  <Label className="text-white font-medium mb-2 block">Post frequency goal (per month)</Label>
                  <Input
                    type="number"
                    value={settings.customMetrics.postFrequencyGoal}
                    onChange={(e) =>
                      updateSetting("customMetrics", "postFrequencyGoal", Number.parseInt(e.target.value))
                    }
                    className="bg-gray-800 border-gray-700 text-white"
                    min={1}
                  />
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-3 block">Benchmark comparisons</Label>
                <div className="space-y-2">
                  {benchmarkOptions.map((option) => (
                    <div key={option.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`benchmark-${option.id}`}
                        checked={settings.customMetrics.benchmarkComparisons.includes(option.id)}
                        onCheckedChange={(checked) => {
                          const currentBenchmarks = settings.customMetrics.benchmarkComparisons
                          const updatedBenchmarks = checked
                            ? [...currentBenchmarks, option.id]
                            : currentBenchmarks.filter((b) => b !== option.id)
                          updateSetting("customMetrics", "benchmarkComparisons", updatedBenchmarks)
                        }}
                      />
                      <Label htmlFor={`benchmark-${option.id}`} className="text-white text-sm">
                        {option.label}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Cancel
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Settings</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
