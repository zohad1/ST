"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CreditCard, BanknoteIcon as Bank, CheckCircle, Download, Plus, Star } from "lucide-react"

interface PaymentSettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function PaymentSettingsModal({ isOpen, onClose }: PaymentSettingsModalProps) {
  const [paymentSettings, setPaymentSettings] = useState({
    frequency: "weekly",
    minThreshold: [50],
    autoPayout: true,
    notifications: true,
  })

  const paymentMethods = [
    {
      id: "stripe-bank",
      type: "bank",
      name: "Bank Account",
      details: "••••1234",
      provider: "Stripe",
      isPrimary: true,
      isVerified: true,
    },
    {
      id: "paypal",
      type: "paypal",
      name: "PayPal",
      details: "alex@email.com",
      provider: "PayPal",
      isPrimary: false,
      isVerified: true,
    },
  ]

  const financialData = {
    totalLifetime: 8540,
    thisMonth: 1247,
    pendingPayouts: 125.3,
    availableBalance: 347.5,
    breakdown: {
      basePay: 6200,
      bonuses: 1340,
      commissions: 750,
      leaderboard: 150,
      referrals: 100,
    },
    lastPayout: {
      amount: 347.5,
      date: "March 15",
    },
    taxInfo: {
      w9Submitted: true,
      taxIdVerified: true,
    },
  }

  const paymentHistory = [
    {
      id: "1",
      campaign: "Summer Fashion Collection",
      amount: 347.5,
      type: "Campaign Payout",
      status: "Completed",
      date: "March 15, 2024",
    },
    {
      id: "2",
      campaign: "Tech Gadget Launch",
      amount: 225.0,
      type: "Base Pay",
      status: "Completed",
      date: "March 8, 2024",
    },
    {
      id: "3",
      campaign: "Beauty Essentials",
      amount: 150.0,
      type: "Bonus",
      status: "Processing",
      date: "March 12, 2024",
    },
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white text-2xl">Payment Settings</DialogTitle>
          <DialogDescription className="text-gray-400">
            Manage your payment methods, payout preferences, and financial information.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-8">
          {/* Payout Methods */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Payout Methods</h3>
              <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Add Payment Method
              </Button>
            </div>

            <div className="space-y-3">
              {paymentMethods.map((method) => (
                <div key={method.id} className="p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-gray-700 rounded-lg">
                        {method.type === "bank" ? (
                          <Bank className="h-5 w-5 text-gray-400" />
                        ) : (
                          <CreditCard className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-white font-medium">
                            {method.provider} - {method.name}
                          </p>
                          {method.isPrimary && (
                            <Badge className="bg-purple-600 text-white">
                              <Star className="h-3 w-3 mr-1" />
                              Primary
                            </Badge>
                          )}
                          {method.isVerified && (
                            <Badge className="bg-green-600 text-white">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Verified
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-400">{method.details}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!method.isPrimary && (
                        <Button variant="outline" size="sm" className="border-gray-600 text-gray-300 bg-transparent">
                          Set as Primary
                        </Button>
                      )}
                      <Button variant="outline" size="sm" className="border-gray-600 text-gray-300 bg-transparent">
                        Edit
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Payout Preferences */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Payout Preferences</h3>
            <div className="space-y-6">
              <div>
                <Label className="text-white font-medium mb-2 block">Payout frequency</Label>
                <Select
                  value={paymentSettings.frequency}
                  onValueChange={(value) => setPaymentSettings((prev) => ({ ...prev, frequency: value }))}
                >
                  <SelectTrigger className="w-48 bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="bi-weekly">Bi-weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-white font-medium mb-3 block">
                  Minimum payout threshold: ${paymentSettings.minThreshold[0]}
                </Label>
                <Slider
                  value={paymentSettings.minThreshold}
                  onValueChange={(value) => setPaymentSettings((prev) => ({ ...prev, minThreshold: value }))}
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

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Auto-payout</Label>
                  <p className="text-sm text-gray-400">Automatically process payouts when threshold is met</p>
                </div>
                <Switch
                  checked={paymentSettings.autoPayout}
                  onCheckedChange={(checked) => setPaymentSettings((prev) => ({ ...prev, autoPayout: checked }))}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white font-medium">Payout notifications</Label>
                  <p className="text-sm text-gray-400">Get notified when payouts are processed</p>
                </div>
                <Switch
                  checked={paymentSettings.notifications}
                  onCheckedChange={(checked) => setPaymentSettings((prev) => ({ ...prev, notifications: checked }))}
                />
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Tax Information */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Tax Information</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <p className="text-white font-medium">Tax forms</p>
                  </div>
                  <p className="text-sm text-gray-400">W-9 Submitted</p>
                </div>
                <div className="p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <p className="text-white font-medium">Tax ID verification</p>
                  </div>
                  <p className="text-sm text-gray-400">Verified</p>
                </div>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" className="border-gray-600 text-gray-300 bg-transparent">
                  Update Tax Info
                </Button>
                <Button variant="outline" className="border-gray-600 text-gray-300 bg-transparent">
                  <Download className="h-4 w-4 mr-2" />
                  Download Tax Documents
                </Button>
              </div>
            </div>
          </div>

          <Separator className="bg-gray-700" />

          {/* Financial History */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Financial History</h3>

            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-400">Total Lifetime</p>
                <p className="text-2xl font-bold text-green-400">${financialData.totalLifetime.toLocaleString()}</p>
              </div>
              <div className="p-4 bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-400">This Month</p>
                <p className="text-2xl font-bold text-purple-400">${financialData.thisMonth.toLocaleString()}</p>
              </div>
              <div className="p-4 bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-400">Pending</p>
                <p className="text-2xl font-bold text-yellow-400">${financialData.pendingPayouts}</p>
              </div>
              <div className="p-4 bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-400">Available</p>
                <p className="text-2xl font-bold text-blue-400">${financialData.availableBalance}</p>
              </div>
            </div>

            {/* Earnings Breakdown */}
            <div className="p-4 bg-gray-800 rounded-lg mb-4">
              <h4 className="text-white font-medium mb-3">Earnings Breakdown</h4>
              <div className="grid grid-cols-5 gap-4">
                <div className="text-center">
                  <p className="text-lg font-semibold text-white">
                    ${financialData.breakdown.basePay.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">Base Pay</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-white">
                    ${financialData.breakdown.bonuses.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">Bonuses</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-white">
                    ${financialData.breakdown.commissions.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">Commissions</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-white">
                    ${financialData.breakdown.leaderboard.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">Leaderboard</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-white">
                    ${financialData.breakdown.referrals.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">Referrals</p>
                </div>
              </div>
            </div>

            {/* Recent Transactions */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <p className="text-white font-medium">Recent Transactions</p>
                <Button variant="outline" size="sm" className="border-gray-600 text-gray-300 bg-transparent">
                  View Full History
                </Button>
              </div>
              <div className="space-y-2">
                {paymentHistory.map((payment) => (
                  <div key={payment.id} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                    <div>
                      <p className="text-white font-medium">{payment.campaign}</p>
                      <p className="text-sm text-gray-400">
                        {payment.type} • {payment.date}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-white font-semibold">${payment.amount}</p>
                      <Badge
                        className={
                          payment.status === "Completed"
                            ? "bg-green-600 text-white"
                            : payment.status === "Processing"
                              ? "bg-yellow-600 text-white"
                              : "bg-gray-600 text-gray-300"
                        }
                      >
                        {payment.status}
                      </Badge>
                    </div>
                  </div>
                ))}
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
