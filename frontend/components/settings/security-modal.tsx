"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Smartphone, Monitor, MapPin, Key } from "lucide-react"

interface SecurityModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SecurityModal({ isOpen, onClose }: SecurityModalProps) {
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [loginNotifications, setLoginNotifications] = useState(true)
  const [suspiciousActivityAlerts, setSuspiciousActivityAlerts] = useState(true)

  const loginActivity = [
    {
      device: "Chrome on Mac",
      location: "San Francisco, CA",
      date: "Current session",
      isCurrent: true,
    },
    {
      device: "iPhone Safari",
      location: "San Francisco, CA",
      date: "2 hours ago",
      isCurrent: false,
    },
    {
      device: "Chrome on Windows",
      location: "Los Angeles, CA",
      date: "3 days ago",
      isCurrent: false,
    },
  ]

  const connectedApps = [
    {
      name: "TikTok Account",
      status: "Connected",
      handle: "@alexjohnson",
      connected: true,
    },
    {
      name: "Discord Account",
      status: "Connected",
      handle: "Alex#1234",
      connected: true,
    },
    {
      name: "Instagram",
      status: "Not Connected",
      handle: "",
      connected: false,
    },
    {
      name: "YouTube",
      status: "Not Connected",
      handle: "",
      connected: false,
    },
  ]

  const activeIntegrations = [
    {
      name: "LaunchPaid Mobile App",
      lastAccess: "2 minutes ago",
      permissions: ["Read profile", "Manage campaigns", "View earnings"],
    },
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Security & Account Access</DialogTitle>
          <DialogDescription className="text-gray-400">
            Manage your account security and monitor access to your account.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Password & Authentication */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Password & Authentication</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Change Password</p>
                  <p className="text-sm text-gray-400">Last changed: 2 months ago</p>
                  <Badge className="bg-green-600 text-white mt-1">Strong</Badge>
                </div>
                <Button variant="outline" className="border-gray-600 text-gray-300 bg-transparent">
                  <Key className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Two-Factor Authentication</Label>
                  <p className="text-sm text-gray-400">Add an extra layer of security to your account</p>
                </div>
                <Switch checked={twoFactorEnabled} onCheckedChange={setTwoFactorEnabled} />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Login Activity */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Login Activity</h3>
            <div className="space-y-4">
              {loginActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-700 rounded-lg">
                      {activity.device.includes("iPhone") ? (
                        <Smartphone className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Monitor className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                    <div>
                      <p className="text-white font-medium">{activity.device}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <MapPin className="h-3 w-3" />
                        <span>{activity.location}</span>
                        <span>•</span>
                        <span>{activity.date}</span>
                      </div>
                    </div>
                  </div>
                  {activity.isCurrent && <Badge className="bg-green-600 text-white">Current</Badge>}
                </div>
              ))}
              <Button variant="outline" className="w-full border-gray-600 text-gray-300 bg-transparent">
                Sign out all other sessions
              </Button>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Connected Apps & Integrations */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Connected Apps & Integrations</h3>
            <div className="space-y-4">
              {connectedApps.map((app, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{app.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={app.connected ? "bg-green-600 text-white" : "bg-gray-600 text-gray-300"}>
                        {app.status}
                      </Badge>
                      {app.handle && <span className="text-sm text-gray-400">({app.handle})</span>}
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className={app.connected ? "border-red-600 text-red-400" : "border-purple-600 text-purple-400"}
                  >
                    {app.connected ? "Disconnect" : "Connect"}
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Account Security */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Account Security</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Login notifications</Label>
                  <p className="text-sm text-gray-400">Get notified when someone signs into your account</p>
                </div>
                <Switch checked={loginNotifications} onCheckedChange={setLoginNotifications} />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Suspicious activity alerts</Label>
                  <p className="text-sm text-gray-400">Get alerts about unusual account activity</p>
                </div>
                <Switch checked={suspiciousActivityAlerts} onCheckedChange={setSuspiciousActivityAlerts} />
              </div>
              <div>
                <Label className="text-white font-medium">Account recovery email</Label>
                <p className="text-sm text-gray-400 mt-1">alex@email.com</p>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* API Access */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">API Access</h3>
            <div className="space-y-4">
              {activeIntegrations.map((integration, index) => (
                <div key={index} className="p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-white font-medium">{integration.name}</p>
                    <Button variant="outline" size="sm" className="border-red-600 text-red-400 bg-transparent">
                      Revoke Access
                    </Button>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">Last access: {integration.lastAccess}</p>
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Permissions:</p>
                    <div className="flex flex-wrap gap-1">
                      {integration.permissions.map((permission, permIndex) => (
                        <Badge key={permIndex} className="bg-gray-700 text-gray-300 text-xs">
                          {permission}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
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
