"use client"

import { useState } from "react"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Bell,
  User,
  Shield,
  Link,
  CreditCard,
  Eye,
  Globe,
  Lock,
  Settings,
  CheckCircle,
  ExternalLink,
  Unlink,
  Users,
  BarChart3,
} from "lucide-react"
import { useTikTokIntegration } from "@/hooks/useTikTokIntegration"
import { useAuth } from "@/hooks/useAuth"

export default function CreatorSettingsPage() {
  const { user } = useAuth()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const { 
    isConnected, 
    connectionStatus, 
    connectTikTok, 
    disconnectTikTok, 
    refreshConnection,
    loading,
    error 
  } = useTikTokIntegration()

  // Notification settings
  const [notifications, setNotifications] = useState({
    campaignUpdates: true,
    paymentNotifications: true,
    deadlineReminders: true,
    newOpportunities: true,
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
  })

  // Privacy settings
  const [privacy, setPrivacy] = useState({
    profileVisibility: 'public',
    showEarnings: false,
    showMetrics: true,
    allowDirectContact: true,
  })

  const handleTikTokConnect = async () => {
    try {
      await connectTikTok()
    } catch (error) {
      console.error('Failed to connect TikTok:', error)
    }
  }

  const handleTikTokDisconnect = async () => {
    try {
      await disconnectTikTok()
    } catch (error) {
      console.error('Failed to disconnect TikTok:', error)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <CreatorSidebar 
        isMobileOpen={isMobileSidebarOpen} 
        onMobileClose={() => setIsMobileSidebarOpen(false)} 
      />

      <div className="lg:ml-60 min-h-screen">
        <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />

        <main className="p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Settings</h1>
            <p className="text-gray-400 text-lg">Manage your account settings and preferences</p>
          </div>

          <Tabs defaultValue="account" className="space-y-6">
            <TabsList className="bg-gray-900 border-gray-800">
              <TabsTrigger value="account" className="data-[state=active]:bg-purple-600">
                Account
              </TabsTrigger>
              <TabsTrigger value="integrations" className="data-[state=active]:bg-purple-600">
                Integrations
              </TabsTrigger>
              <TabsTrigger value="notifications" className="data-[state=active]:bg-purple-600">
                Notifications
              </TabsTrigger>
              <TabsTrigger value="privacy" className="data-[state=active]:bg-purple-600">
                Privacy
              </TabsTrigger>
              <TabsTrigger value="payments" className="data-[state=active]:bg-purple-600">
                Payments
              </TabsTrigger>
            </TabsList>

            <TabsContent value="account">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5 text-purple-400" />
                      Profile Information
                    </CardTitle>
                    <CardDescription>Update your personal information and profile details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Full Name</label>
                        <Input 
                          defaultValue={user?.display_name || user?.username || ""} 
                          className="bg-gray-800 border-gray-700"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Username</label>
                        <Input 
                          defaultValue={user?.username || ""} 
                          className="bg-gray-800 border-gray-700"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Email</label>
                        <Input 
                          defaultValue={user?.email || ""} 
                          className="bg-gray-800 border-gray-700"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Phone</label>
                        <Input 
                          defaultValue={(user as any)?.phone || ""} 
                          className="bg-gray-800 border-gray-700"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Bio</label>
                      <textarea 
                        className="w-full p-3 bg-gray-800 border border-gray-700 rounded-md text-white"
                        rows={4}
                        defaultValue={(user as any)?.bio || ""}
                        placeholder="Tell us about yourself..."
                      />
                    </div>
                    <Button className="bg-purple-600 hover:bg-purple-700">
                      Save Changes
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="integrations">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Link className="h-5 w-5 text-purple-400" />
                      Social Media Integrations
                    </CardTitle>
                    <CardDescription>Connect your social media accounts to sync content and analytics</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* TikTok Integration */}
                    <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-black rounded-lg flex items-center justify-center">
                          <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-.88-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43V7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.43z"/>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-semibold">TikTok</h3>
                          <p className="text-sm text-gray-400">
                            {isConnected ? 'Connected and syncing' : 'Connect to sync your TikTok content and analytics'}
                          </p>
                          {connectionStatus && (
                            <div className="flex items-center gap-2 mt-1">
                              <Badge 
                                className={
                                  connectionStatus.status === 'active' 
                                    ? 'bg-green-600' 
                                    : connectionStatus.status === 'error'
                                    ? 'bg-red-600'
                                    : 'bg-yellow-600'
                                }
                              >
                                {connectionStatus.status}
                              </Badge>
                              {connectionStatus.username && (
                                <span className="text-xs text-gray-400">@{connectionStatus.username}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {isConnected ? (
                          <>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={refreshConnection}
                              disabled={loading}
                            >
                              <BarChart3 className="h-4 w-4 mr-2" />
                              Sync
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={handleTikTokDisconnect}
                              disabled={loading}
                              className="text-red-400 hover:text-red-300"
                            >
                              <Unlink className="h-4 w-4 mr-2" />
                              Disconnect
                            </Button>
                          </>
                        ) : (
                          <Button 
                            onClick={handleTikTokConnect}
                            disabled={loading}
                            className="bg-purple-600 hover:bg-purple-700"
                          >
                            <ExternalLink className="h-4 w-4 mr-2" />
                            Connect TikTok
                          </Button>
                        )}
                      </div>
                    </div>

                    {/* Instagram Integration */}
                    <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-gradient-to-br from-purple-500 via-pink-500 to-yellow-500 rounded-lg flex items-center justify-center">
                          <svg className="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-semibold">Instagram</h3>
                          <p className="text-sm text-gray-400">Connect to sync your Instagram content and analytics</p>
                          <Badge className="bg-gray-600 mt-1">Coming Soon</Badge>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" disabled>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Connect
                      </Button>
                    </div>

                    {/* YouTube Integration */}
                    <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-red-600 rounded-lg flex items-center justify-center">
                          <svg className="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-semibold">YouTube</h3>
                          <p className="text-sm text-gray-400">Connect to sync your YouTube content and analytics</p>
                          <Badge className="bg-gray-600 mt-1">Coming Soon</Badge>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" disabled>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Connect
                      </Button>
                    </div>

                    {error && (
                      <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                        <p className="text-red-400 text-sm">{error}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="notifications">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Bell className="h-5 w-5 text-purple-400" />
                      Notification Preferences
                    </CardTitle>
                    <CardDescription>Choose what notifications you want to receive</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Campaign Updates</h4>
                          <p className="text-sm text-gray-400">Get notified about campaign status changes</p>
                        </div>
                        <Switch 
                          checked={notifications.campaignUpdates}
                          onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, campaignUpdates: checked }))}
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Payment Notifications</h4>
                          <p className="text-sm text-gray-400">Get notified about payments and payouts</p>
                        </div>
                        <Switch 
                          checked={notifications.paymentNotifications}
                          onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, paymentNotifications: checked }))}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Deadline Reminders</h4>
                          <p className="text-sm text-gray-400">Get reminded about upcoming deliverable deadlines</p>
                        </div>
                        <Switch 
                          checked={notifications.deadlineReminders}
                          onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, deadlineReminders: checked }))}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">New Opportunities</h4>
                          <p className="text-sm text-gray-400">Get notified about new campaign opportunities</p>
                        </div>
                        <Switch 
                          checked={notifications.newOpportunities}
                          onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, newOpportunities: checked }))}
                        />
                      </div>
                    </div>

                    <div className="border-t border-gray-700 pt-4">
                      <h4 className="font-medium mb-4">Delivery Methods</h4>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-medium">Email Notifications</h5>
                            <p className="text-sm text-gray-400">Receive notifications via email</p>
                          </div>
                          <Switch 
                            checked={notifications.emailNotifications}
                            onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, emailNotifications: checked }))}
                          />
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-medium">SMS Notifications</h5>
                            <p className="text-sm text-gray-400">Receive urgent notifications via SMS</p>
                          </div>
                          <Switch 
                            checked={notifications.smsNotifications}
                            onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, smsNotifications: checked }))}
                          />
                        </div>

                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-medium">Push Notifications</h5>
                            <p className="text-sm text-gray-400">Receive notifications in your browser</p>
                          </div>
                          <Switch 
                            checked={notifications.pushNotifications}
                            onCheckedChange={(checked) => setNotifications(prev => ({ ...prev, pushNotifications: checked }))}
                          />
                        </div>
                      </div>
                    </div>

                    <Button className="bg-purple-600 hover:bg-purple-700">
                      Save Preferences
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="privacy">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5 text-purple-400" />
                      Privacy Settings
                    </CardTitle>
                    <CardDescription>Control how your information is shared and displayed</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Profile Visibility</h4>
                        <select 
                          className="w-full p-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                          value={privacy.profileVisibility}
                          onChange={(e) => setPrivacy(prev => ({ ...prev, profileVisibility: e.target.value }))}
                        >
                          <option value="public">Public - Anyone can view</option>
                          <option value="brands">Brands Only - Only verified brands can view</option>
                          <option value="private">Private - Only you can view</option>
                        </select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Show Earnings</h4>
                          <p className="text-sm text-gray-400">Display your earnings on your public profile</p>
                        </div>
                        <Switch 
                          checked={privacy.showEarnings}
                          onCheckedChange={(checked) => setPrivacy(prev => ({ ...prev, showEarnings: checked }))}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Show Performance Metrics</h4>
                          <p className="text-sm text-gray-400">Display your performance metrics to brands</p>
                        </div>
                        <Switch 
                          checked={privacy.showMetrics}
                          onCheckedChange={(checked) => setPrivacy(prev => ({ ...prev, showMetrics: checked }))}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Allow Direct Contact</h4>
                          <p className="text-sm text-gray-400">Allow brands to contact you directly</p>
                        </div>
                        <Switch 
                          checked={privacy.allowDirectContact}
                          onCheckedChange={(checked) => setPrivacy(prev => ({ ...prev, allowDirectContact: checked }))}
                        />
                      </div>
                    </div>

                    <Button className="bg-purple-600 hover:bg-purple-700">
                      Save Settings
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="payments">
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CreditCard className="h-5 w-5 text-purple-400" />
                      Payment Settings
                    </CardTitle>
                    <CardDescription>Manage your payment methods and preferences</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
                          <CreditCard className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold">Stripe Account</h3>
                          <p className="text-sm text-gray-400">Connected for automatic payouts</p>
                          <Badge className="bg-green-600 mt-1">Connected</Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-400" />
                        <Button variant="outline" size="sm">
                          Manage
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Payout Schedule</h4>
                        <select className="w-full p-2 bg-gray-800 border border-gray-700 rounded-md text-white">
                          <option value="weekly">Weekly (Every Friday)</option>
                          <option value="biweekly">Bi-weekly (Every other Friday)</option>
                          <option value="monthly">Monthly (1st of each month)</option>
                        </select>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Minimum Payout Amount</h4>
                        <select className="w-full p-2 bg-gray-800 border border-gray-700 rounded-md text-white">
                          <option value="50">$50</option>
                          <option value="100">$100</option>
                          <option value="250">$250</option>
                          <option value="500">$500</option>
                        </select>
                      </div>
                    </div>

                    <Button className="bg-purple-600 hover:bg-purple-700">
                      Save Payment Settings
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}
