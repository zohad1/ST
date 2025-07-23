"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { CheckCircle, Download, Edit, Trash2 } from "lucide-react"

interface AccountModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AccountModal({ isOpen, onClose }: AccountModalProps) {
  const [isDeactivating, setIsDeactivating] = useState(false)

  const accountData = {
    name: "Alex Johnson",
    email: "alex@email.com",
    phone: "+1 (555) 123-4567",
    dateJoined: "January 2024",
    status: "Active Creator",
    profileCompletion: 85,
    missingItems: ["Add shipping address", "Verify Discord"],
    stats: {
      totalCampaigns: 12,
      totalEarnings: 8540,
      gmvGenerated: 125400,
      badgeLevel: "$100K+ GMV",
    },
    lastBackup: "March 15, 2024",
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Your Account</DialogTitle>
          <DialogDescription className="text-gray-400">Manage your account information and data.</DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Profile Information */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Profile Information</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Creator Name</label>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-white">{accountData.name}</span>
                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                      <Edit className="h-3 w-3 text-gray-400" />
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Email</label>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-white">{accountData.email}</span>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Phone</label>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-white">{accountData.phone}</span>
                    <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                      <Edit className="h-3 w-3 text-gray-400" />
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Date Joined</label>
                  <p className="text-white mt-1">{accountData.dateJoined}</p>
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Account Status</label>
                <div className="mt-1">
                  <Badge className="bg-green-600 text-white">{accountData.status}</Badge>
                </div>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Profile Completion */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Profile Completion</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white">Progress</span>
                  <span className="text-purple-400 font-semibold">{accountData.profileCompletion}%</span>
                </div>
                <Progress value={accountData.profileCompletion} className="h-2" />
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">Missing items:</p>
                <ul className="space-y-1">
                  {accountData.missingItems.map((item, index) => (
                    <li key={index} className="text-sm text-orange-400">
                      • {item}
                    </li>
                  ))}
                </ul>
              </div>
              <Button className="bg-purple-600 hover:bg-purple-700 text-white">Complete Profile</Button>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Account Statistics */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Account Statistics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400">Total Campaigns</p>
                <p className="text-2xl font-bold text-white">{accountData.stats.totalCampaigns}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400">Total Earnings</p>
                <p className="text-2xl font-bold text-green-400">${accountData.stats.totalEarnings.toLocaleString()}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400">GMV Generated</p>
                <p className="text-2xl font-bold text-purple-400">${accountData.stats.gmvGenerated.toLocaleString()}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-sm text-gray-400">Badge Level</p>
                <p className="text-lg font-bold text-yellow-400">{accountData.stats.badgeLevel}</p>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Data Management */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Data Management</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Download Data Archive</p>
                  <p className="text-sm text-gray-400">Export all your LaunchPaid data</p>
                </div>
                <Button variant="outline" className="border-gray-600 text-gray-300 bg-transparent">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Export Earnings Report</p>
                  <p className="text-sm text-gray-400">Download detailed earnings history</p>
                </div>
                <Button variant="outline" className="border-gray-600 text-gray-300 bg-transparent">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
              <div>
                <p className="text-sm text-gray-400">Last backup: {accountData.lastBackup}</p>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Account Actions */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Account Actions</h3>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-300 bg-transparent">
                <Edit className="h-4 w-4 mr-2" />
                Update Email
              </Button>
              <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-300 bg-transparent">
                <Edit className="h-4 w-4 mr-2" />
                Change Username
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start border-red-600 text-red-400 hover:bg-red-600 hover:text-white bg-transparent"
                onClick={() => setIsDeactivating(true)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Deactivate Account
              </Button>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6">
          <Button variant="outline" onClick={onClose} className="border-gray-600 text-gray-300 bg-transparent">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
