"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Monitor, Sun, Moon, Globe, Accessibility } from "lucide-react"

interface DisplayModalProps {
  isOpen: boolean
  onClose: () => void
}

export function DisplayModal({ isOpen, onClose }: DisplayModalProps) {
  const [displaySettings, setDisplaySettings] = useState({
    theme: "dark",
    fontSize: "medium",
    highContrast: false,
    reduceMotion: false,
    language: "english",
    dateFormat: "mm-dd-yyyy",
    numberFormat: "us",
    accessibility: {
      screenReader: false,
      keyboardNavigation: true,
      colorBlindFriendly: false,
      audioDescriptions: false,
    },
  })

  const updateSetting = (key: string, value: any) => {
    setDisplaySettings((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  const updateAccessibilitySetting = (key: string, value: boolean) => {
    setDisplaySettings((prev) => ({
      ...prev,
      accessibility: {
        ...prev.accessibility,
        [key]: value,
      },
    }))
  }

  const fontSizeOptions = [
    { value: "small", label: "Small", preview: "text-sm" },
    { value: "medium", label: "Medium", preview: "text-base" },
    { value: "large", label: "Large", preview: "text-lg" },
    { value: "extra-large", label: "Extra Large", preview: "text-xl" },
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Display & Accessibility</DialogTitle>
          <DialogDescription className="text-gray-400">
            Customize how LaunchPaid content is displayed and configure accessibility options.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Display Preferences */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Monitor className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Display Preferences</h3>
            </div>
            <div className="space-y-6">
              <div>
                <Label className="text-white font-medium mb-3 block">Theme</Label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => updateSetting("theme", "dark")}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      displaySettings.theme === "dark"
                        ? "border-purple-600 bg-purple-600/20"
                        : "border-gray-700 bg-gray-800"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Moon className="h-4 w-4 text-white" />
                      <span className="text-white font-medium">Dark</span>
                    </div>
                    <div className="text-sm text-gray-400">Current theme</div>
                  </button>
                  <button
                    onClick={() => updateSetting("theme", "light")}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      displaySettings.theme === "light"
                        ? "border-purple-600 bg-purple-600/20"
                        : "border-gray-700 bg-gray-800"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Sun className="h-4 w-4 text-white" />
                      <span className="text-white font-medium">Light</span>
                    </div>
                    <div className="text-sm text-gray-400">Coming soon</div>
                  </button>
                  <button
                    onClick={() => updateSetting("theme", "auto")}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      displaySettings.theme === "auto"
                        ? "border-purple-600 bg-purple-600/20"
                        : "border-gray-700 bg-gray-800"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Monitor className="h-4 w-4 text-white" />
                      <span className="text-white font-medium">Auto</span>
                    </div>
                    <div className="text-sm text-gray-400">System preference</div>
                  </button>
                </div>
              </div>

              <div>
                <Label className="text-white font-medium mb-3 block">Font size</Label>
                <div className="grid grid-cols-2 gap-3">
                  {fontSizeOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => updateSetting("fontSize", option.value)}
                      className={`p-4 rounded-lg border-2 text-left transition-colors ${
                        displaySettings.fontSize === option.value
                          ? "border-purple-600 bg-purple-600/20"
                          : "border-gray-700 bg-gray-800"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">{option.label}</span>
                        {displaySettings.fontSize === option.value && (
                          <span className="text-purple-400 text-sm">(Current)</span>
                        )}
                      </div>
                      <div className={`text-gray-400 ${option.preview}`}>Sample text preview</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">High contrast mode</Label>
                  <p className="text-sm text-gray-400">Increase contrast for better visibility</p>
                </div>
                <Switch
                  checked={displaySettings.highContrast}
                  onCheckedChange={(checked) => updateSetting("highContrast", checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Reduce motion</Label>
                  <p className="text-sm text-gray-400">Minimize animations and transitions</p>
                </div>
                <Switch
                  checked={displaySettings.reduceMotion}
                  onCheckedChange={(checked) => updateSetting("reduceMotion", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Language Settings */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Globe className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Language Settings</h3>
            </div>
            <div className="space-y-4">
              <div>
                <Label className="text-white font-medium mb-2 block">Primary language</Label>
                <Select value={displaySettings.language} onValueChange={(value) => updateSetting("language", value)}>
                  <SelectTrigger className="w-64 bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="english">English</SelectItem>
                    <SelectItem value="spanish" disabled>
                      Spanish (Coming soon)
                    </SelectItem>
                    <SelectItem value="french" disabled>
                      French (Coming soon)
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-white font-medium mb-2 block">Date format</Label>
                  <Select
                    value={displaySettings.dateFormat}
                    onValueChange={(value) => updateSetting("dateFormat", value)}
                  >
                    <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="mm-dd-yyyy">MM/DD/YYYY</SelectItem>
                      <SelectItem value="dd-mm-yyyy">DD/MM/YYYY</SelectItem>
                      <SelectItem value="yyyy-mm-dd">YYYY-MM-DD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-white font-medium mb-2 block">Number format</Label>
                  <Select
                    value={displaySettings.numberFormat}
                    onValueChange={(value) => updateSetting("numberFormat", value)}
                  >
                    <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="us">US (1,234.56)</SelectItem>
                      <SelectItem value="international">International (1.234,56)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Accessibility */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Accessibility className="h-5 w-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Accessibility</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Screen reader support</Label>
                  <p className="text-sm text-gray-400">Optimize interface for screen readers</p>
                </div>
                <Switch
                  checked={displaySettings.accessibility.screenReader}
                  onCheckedChange={(checked) => updateAccessibilitySetting("screenReader", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Keyboard navigation</Label>
                  <p className="text-sm text-gray-400">Enable full keyboard navigation support</p>
                </div>
                <Switch
                  checked={displaySettings.accessibility.keyboardNavigation}
                  onCheckedChange={(checked) => updateAccessibilitySetting("keyboardNavigation", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Color blind friendly</Label>
                  <p className="text-sm text-gray-400">Use color blind friendly color schemes</p>
                </div>
                <Switch
                  checked={displaySettings.accessibility.colorBlindFriendly}
                  onCheckedChange={(checked) => updateAccessibilitySetting("colorBlindFriendly", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Audio descriptions</Label>
                  <p className="text-sm text-gray-400">Enable audio descriptions for visual content</p>
                </div>
                <Switch
                  checked={displaySettings.accessibility.audioDescriptions}
                  onCheckedChange={(checked) => updateAccessibilitySetting("audioDescriptions", checked)}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Preview Section */}
          <div className="p-4 bg-gray-800 rounded-lg">
            <h4 className="text-white font-medium mb-3">Preview</h4>
            <div className="space-y-2">
              <div
                className={`p-3 bg-gray-700 rounded ${
                  displaySettings.fontSize === "small"
                    ? "text-sm"
                    : displaySettings.fontSize === "large"
                      ? "text-lg"
                      : displaySettings.fontSize === "extra-large"
                        ? "text-xl"
                        : "text-base"
                }`}
              >
                <p className="text-white font-medium">Campaign Performance</p>
                <p className="text-gray-400">
                  {displaySettings.dateFormat === "mm-dd-yyyy"
                    ? "03/15/2024"
                    : displaySettings.dateFormat === "dd-mm-yyyy"
                      ? "15/03/2024"
                      : "2024-03-15"}
                </p>
                <p className="text-green-400">{displaySettings.numberFormat === "us" ? "$1,234.56" : "$1.234,56"}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Cancel
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Apply Settings</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
