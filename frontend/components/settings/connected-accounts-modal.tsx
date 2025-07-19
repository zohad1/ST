"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { CheckCircle, X, MessageSquare, Video, Camera, RefreshCw } from "lucide-react"

interface ConnectedAccountsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ConnectedAccountsModal({ isOpen, onClose }: ConnectedAccountsModalProps) {
  const [accounts, setAccounts] = useState({
    tiktok: {
      connected: true,
      handle: "@alexjohnson",
      followers: "125.4K",
      lastSync: "2 minutes ago",
      dataSyncEnabled: true,
      crossPostingEnabled: false,
    },
    discord: {
      connected: true,
      username: "Alex#1234",
      serverRoles: ["Creator", "Verified"],
      lastSync: "5 minutes ago",
      dataSyncEnabled: true,
    },
    instagram: {
      connected: false,
      benefits: ["Cross-platform campaigns", "Expanded reach", "Story integrations"],
    },
    youtube: {
      connected: false,
      benefits: ["Video campaign opportunities", "Long-form content", "Monetization tracking"],
    },
  })

  const [connectionSettings, setConnectionSettings] = useState({
    autoSync: true,
    privacyMode: false,
    crossPosting: false,
  })

  const handleConnect = (platform: string) => {
    // In a real app, this would trigger OAuth flow
    console.log(`Connecting to ${platform}...`)
  }

  const handleDisconnect = (platform: string) => {
    setAccounts((prev) => ({
      ...prev,
      [platform]: {
        ...prev[platform as keyof typeof prev],
        connected: false,
      },
    }))
  }

  const handleReconnect = (platform: string) => {
    console.log(`Reconnecting to ${platform}...`)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Connected Accounts</DialogTitle>
          <DialogDescription className="text-gray-400">
            Manage your social media connections and platform integrations.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Primary Accounts */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Primary Accounts</h3>

            {/* TikTok Account */}
            <div className="p-6 bg-gray-800 rounded-lg mb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-black rounded-lg">
                    <Video className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-lg">TikTok Account</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className="bg-green-600 text-white">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Connected
                      </Badge>
                      <span className="text-gray-400 text-sm">Handle: {accounts.tiktok.handle}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleReconnect("tiktok")}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reconnect
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDisconnect("tiktok")}>
                    Disconnect
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-400">{accounts.tiktok.followers}</p>
                  <p className="text-sm text-gray-400">Followers</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-400">Last sync</p>
                  <p className="text-white">{accounts.tiktok.lastSync}</p>
                </div>
                <div className="text-center">
                  <Button variant="outline" size="sm" className="border-purple-600 text-purple-400 bg-transparent">
                    View Profile
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-white">Data sync preferences</Label>
                  <Switch
                    checked={accounts.tiktok.dataSyncEnabled}
                    onCheckedChange={(checked) =>
                      setAccounts((prev) => ({
                        ...prev,
                        tiktok: { ...prev.tiktok, dataSyncEnabled: checked },
                      }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-white">Automatic content cross-posting</Label>
                  <Switch
                    checked={accounts.tiktok.crossPostingEnabled}
                    onCheckedChange={(checked) =>
                      setAccounts((prev) => ({
                        ...prev,
                        tiktok: { ...prev.tiktok, crossPostingEnabled: checked },
                      }))
                    }
                  />
                </div>
              </div>
            </div>

            {/* Discord Account */}
            <div className="p-6 bg-gray-800 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-indigo-600 rounded-lg">
                    <MessageSquare className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-lg">Discord Account</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className="bg-green-600 text-white">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Connected
                      </Badge>
                      <span className="text-gray-400 text-sm">Username: {accounts.discord.username}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    Update Permissions
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDisconnect("discord")}>
                    Disconnect
                  </Button>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-400 mb-2">Server roles:</p>
                <div className="flex gap-2">
                  {accounts.discord.serverRoles.map((role, index) => (
                    <Badge key={index} className="bg-indigo-600/20 text-indigo-400">
                      {role}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <Label className="text-white">Data sync preferences</Label>
                <Switch
                  checked={accounts.discord.dataSyncEnabled}
                  onCheckedChange={(checked) =>
                    setAccounts((prev) => ({
                      ...prev,
                      discord: { ...prev.discord, dataSyncEnabled: checked },
                    }))
                  }
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Additional Platforms */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Additional Platforms</h3>

            {/* Instagram */}
            <div className="p-6 bg-gray-800 rounded-lg mb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                    <Camera className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-lg">Instagram</h4>
                    <Badge className="bg-gray-600 text-gray-300 mt-1">
                      <X className="h-3 w-3 mr-1" />
                      Not Connected
                    </Badge>
                  </div>
                </div>
                <Button
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                  onClick={() => handleConnect("instagram")}
                >
                  Connect Instagram
                </Button>
              </div>

              <div>
                <p className="text-sm text-gray-400 mb-2">Benefits:</p>
                <ul className="space-y-1">
                  {accounts.instagram.benefits.map((benefit, index) => (
                    <li key={index} className="text-sm text-gray-300">
                      • {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* YouTube */}
            <div className="p-6 bg-gray-800 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-red-600 rounded-lg">
                    <Video className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-lg">YouTube</h4>
                    <Badge className="bg-gray-600 text-gray-300 mt-1">
                      <X className="h-3 w-3 mr-1" />
                      Not Connected
                    </Badge>
                  </div>
                </div>
                <Button
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                  onClick={() => handleConnect("youtube")}
                >
                  Connect YouTube
                </Button>
              </div>

              <div>
                <p className="text-sm text-gray-400 mb-2">Benefits:</p>
                <ul className="space-y-1">
                  {accounts.youtube.benefits.map((benefit, index) => (
                    <li key={index} className="text-sm text-gray-300">
                      • {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Connection Management */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Connection Management</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Automatic data synchronization</Label>
                  <p className="text-sm text-gray-400">Keep all connected accounts synced automatically</p>
                </div>
                <Switch
                  checked={connectionSettings.autoSync}
                  onCheckedChange={(checked) => setConnectionSettings((prev) => ({ ...prev, autoSync: checked }))}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Privacy mode</Label>
                  <p className="text-sm text-gray-400">Limit data sharing between platforms</p>
                </div>
                <Switch
                  checked={connectionSettings.privacyMode}
                  onCheckedChange={(checked) => setConnectionSettings((prev) => ({ ...prev, privacyMode: checked }))}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Cross-platform posting</Label>
                  <p className="text-sm text-gray-400">Enable posting to multiple platforms simultaneously</p>
                </div>
                <Switch
                  checked={connectionSettings.crossPosting}
                  onCheckedChange={(checked) => setConnectionSettings((prev) => ({ ...prev, crossPosting: checked }))}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Close
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Changes</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
