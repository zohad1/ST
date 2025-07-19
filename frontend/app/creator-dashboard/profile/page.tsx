"use client"

import { useState, useEffect } from "react"
import { CreatorSidebar } from "@/components/creator/navigation/creator-sidebar"
import { CreatorHeader } from "@/components/creator/navigation/creator-header"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  CheckCircle,
  AlertCircle,
  MapPin,
  Users,
  TrendingUp,
  Award,
  Settings,
  Shield,
  Bell,
  LinkIcon,
  Star,
  Target,
  Calendar,
  User,
  Camera,
  Upload,
  Loader2,
  XCircle,
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useProfile } from "@/hooks/useProfile"
import { useDemographics } from "@/hooks/useDemographics"
import { usePerformance } from "@/hooks/usePerformance"
import { toast } from "@/components/ui/use-toast"
import { userServiceClient } from "@/lib/api/client"

// Constants
const NICHES = [
  "Beauty & Care",
  "Fashion",
  "Fitness & Health", 
  "Food & Cooking",
  "Technology",
  "Home & Living",
  "Outdoor & Sports",
  "Collectibles & Toys",
  "Entertainment",
  "Education",
  "Lifestyle",
  "Travel",
  "Gaming",
  "DIY & Crafts",
  "Parenting",
  "Finance",
  "Art & Design",
  "Music",
  "Pets",
  "Business"
]

const CONTENT_STYLES = [
  "Educational",
  "Entertainment", 
  "Reviews",
  "Tutorials",
  "Vlogs",
  "Comedy",
  "Inspirational",
  "Behind the Scenes",
  "Product Demos",
  "Unboxing",
  "Challenges",
  "Q&A"
]

export default function CreatorProfilePage() {
  const router = useRouter()
  const { user, refreshUser } = useAuth()
  const { profile, loading: profileLoading, error: profileError, updating: profileUpdating, updateProfile, fetchProfile } = useProfile()
  const { demographics, summary, loading: demographicsLoading, error: demographicsError, createDemographics } = useDemographics()
  const { performance, loading: performanceLoading, error: performanceError, fetchPerformance } = usePerformance()
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  
  // Debug logging for user and performance
  useEffect(() => {
    console.log('🔍 CreatorProfilePage: user =', user)
    console.log('🔍 CreatorProfilePage: user?.id =', user?.id)
    console.log('🔍 CreatorProfilePage: performance =', performance)
    console.log('🔍 CreatorProfilePage: performanceLoading =', performanceLoading)
    console.log('🔍 CreatorProfilePage: performanceError =', performanceError)
  }, [user, performance, performanceLoading, performanceError])

  const [profileData, setProfileData] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    gender: "",
    bio: "",
    avatar_url: "",
    date_of_birth: "",
    // Social media handles
    tiktok_handle: "",
    instagram_handle: "",
    discord_handle: "",
    // Address fields
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "United States",
    // Creator specific fields
    content_niche: "",
    follower_count: 0,
    average_views: 0,
    engagement_rate: 0,
    // Frontend only fields
    primary_niche: "",
    secondary_niches: [] as string[],
    content_style: [] as string[],
    audienceDemographics: false,
  })

  const [notifications, setNotifications] = useState({
    sms: true,
    email: true,
    inApp: true,
    campaigns: true,
    payments: true,
    opportunities: true,
    performance: false,
  })

  // Calculate completion items based on real data
  const completionItems = [
    { 
      name: "Basic Info Complete", 
      completed: !!(profileData.first_name && profileData.last_name && profileData.email && profileData.phone), 
      description: "Name, email, phone" 
    },
    { 
      name: "TikTok Connected", 
      completed: !!profileData.tiktok_handle, 
      description: "Handle and account verification" 
    },
    { 
      name: "Discord Connected", 
      completed: !!profileData.discord_handle, 
      description: "Handle and server membership" 
    },
    { 
      name: "Shipping Address", 
      completed: !!(profileData.address_line1 && profileData.city && profileData.state && profileData.postal_code), 
      description: "Required for sample shipping" 
    },
    { 
      name: "Audience Demographics", 
      completed: !!(summary && summary.total_entries > 0), 
      description: "Required for campaign matching" 
    },
    { 
      name: "Content Niches", 
      completed: !!profileData.primary_niche, 
      description: "Required for campaign targeting" 
    },
    { 
      name: "Bio & Description", 
      completed: !!profileData.bio && profileData.bio.length > 10, 
      description: "Tell brands about yourself" 
    },
    { 
      name: "Profile Picture", 
      completed: !!profileData.avatar_url, 
      description: "Add a professional photo" 
    },
  ]

  // Calculate completion percentage based on real data
  const completionPercentage = Math.round((completionItems.filter(item => item.completed).length / completionItems.length) * 100)
  const incompleteItems = completionItems.filter(item => !item.completed).length

  // Debug logging for completion calculation
  useEffect(() => {
    console.log('📋 Profile completion calculation:')
    console.log('📋 Profile data:', {
      first_name: profileData.first_name,
      last_name: profileData.last_name,
      email: profileData.email,
      phone: profileData.phone,
      tiktok_handle: profileData.tiktok_handle,
      discord_handle: profileData.discord_handle,
      address_line1: profileData.address_line1,
      city: profileData.city,
      state: profileData.state,
      postal_code: profileData.postal_code,
      primary_niche: profileData.primary_niche,
      bio: profileData.bio,
      avatar_url: profileData.avatar_url,
    })
    console.log('📋 Demographics summary:', summary)
    console.log('📋 Completion items:', completionItems)
    console.log('📋 Completion percentage:', completionPercentage)
    console.log('📋 Incomplete items count:', incompleteItems)
  }, [profileData, summary, completionItems, completionPercentage, incompleteItems])

  // Use real performance data instead of mock data
  const performanceMetrics = {
    totalGMV: performance?.total_gmv ? `$${parseFloat(performance.total_gmv).toLocaleString()}` : "$0",
    consistency: performance?.consistency_score ? `${(parseFloat(performance.consistency_score) * 100).toFixed(0)}%` : "0%",
    rating: performance?.reliability_rating ? parseFloat(performance.reliability_rating).toFixed(1) : "0.0",
    campaignsCompleted: performance?.completed_deliverables || 0,
    activeCampaigns: 3, // This would come from campaign service
    followers: profileData.follower_count ? profileData.follower_count.toLocaleString() : "0",
  }

  // Debug logging for performance data
  useEffect(() => {
    if (performance) {
      console.log('📊 Performance data loaded:', performance)
      console.log('📊 Calculated metrics:', performanceMetrics)
    }
  }, [performance, performanceMetrics])

  const badges = [
    { 
      name: "$5K GMV Badge", 
      earned: performance?.total_gmv ? parseFloat(performance.total_gmv) >= 5000 : false, 
      color: "bg-purple-600" 
    },
    { 
      name: "$10K GMV Badge", 
      earned: performance?.total_gmv ? parseFloat(performance.total_gmv) >= 10000 : false, 
      progress: performance?.total_gmv ? Math.min((parseFloat(performance.total_gmv) / 10000) * 100, 100) : 0, 
      color: performance?.total_gmv && parseFloat(performance.total_gmv) >= 10000 ? "bg-purple-600" : "bg-gray-600" 
    },
    { 
      name: "Consistency Pro", 
      earned: performance?.consistency_score ? parseFloat(performance.consistency_score) >= 0.8 : false, 
      color: "bg-green-600" 
    },
    { 
      name: "Top Performer", 
      earned: performance?.reliability_rating ? parseFloat(performance.reliability_rating) >= 4.5 : false, 
      progress: performance?.reliability_rating ? (parseFloat(performance.reliability_rating) / 5) * 100 : 0, 
      color: performance?.reliability_rating && parseFloat(performance.reliability_rating) >= 4.5 ? "bg-green-600" : "bg-gray-600" 
    },
  ]

  // Update profile data when backend data loads
  useEffect(() => {
    if (profile) {
      console.log('🔍 Profile data received:', profile)
      console.log('🔍 Content niche from backend:', profile.content_niche)
      
      setProfileData(prev => {
        const newData = {
          ...prev,
          username: profile.username || "",
          first_name: profile.firstName || profile.first_name || "",
          last_name: profile.lastName || profile.last_name || "",
          email: profile.email || user?.email || "",
          phone: profile.phone || "",
          gender: profile.gender || "",
          bio: profile.bio || "",
          date_of_birth: profile.date_of_birth || "",
          tiktok_handle: profile.tiktok_handle || "",
          instagram_handle: profile.instagram_handle || "",
          discord_handle: profile.discord_handle || "",
          avatar_url: profile.profile_image_url || "",
          // Address fields
          address_line1: profile.address_line1 || "",
          address_line2: profile.address_line2 || "",
          city: profile.city || "",
          state: profile.state || "",
          postal_code: profile.postal_code || "",
          country: profile.country || "",
          // Creator specific fields
          content_niche: profile.content_niche || "",
          follower_count: profile.follower_count || 0,
          average_views: profile.average_views || 0,
          engagement_rate: profile.engagement_rate || 0,
          // Map content_niche to primary_niche for frontend compatibility
          primary_niche: profile.content_niche || "",
          // Keep secondary_niches and content_style as arrays for frontend
          secondary_niches: prev.secondary_niches,
          content_style: prev.content_style,
        }
        
        console.log('🔍 Setting profile data with content niche:', newData.primary_niche)
        return newData
      })
    }
  }, [profile, user])

  // Refresh profile data when user changes
  useEffect(() => {
    if (user?.id) {
      fetchProfile()
    }
  }, [user?.id])

  const audienceData = {
    gender: summary?.gender_distribution || { female: 67, male: 33 },
    age: summary?.age_distribution || { "18-24": 45, "25-34": 35, "35-44": 15, "45+": 5 },
    locations: summary?.country_distribution ? 
      Object.entries(summary.country_distribution)
        .map(([country, percentage]) => `${country} (${percentage}%)`)
        .join(', ') : 
      "United States (78%), Canada (12%), UK (10%)",
  }

  const handleSaveProfile = async () => {
    try {
      const updateData = {
        first_name: profileData.first_name || "",
        last_name: profileData.last_name || "",
        phone: profileData.phone || "",
        gender: profileData.gender || "",
        bio: profileData.bio || "",
        tiktok_handle: profileData.tiktok_handle || "",
        instagram_handle: profileData.instagram_handle || "",
        discord_handle: profileData.discord_handle || "",
        date_of_birth: profileData.date_of_birth || "",
        // Address fields
        address_line1: profileData.address_line1 || "",
        address_line2: profileData.address_line2 || "",
        city: profileData.city || "",
        state: profileData.state || "",
        postal_code: profileData.postal_code || "",
        country: profileData.country || "",
        // Creator specific fields
        content_niche: profileData.primary_niche || profileData.content_niche || "",
      }

      console.log('📝 Sending profile update:', updateData)

      const result = await updateProfile(updateData)
      
      if (result.success) {
        // Refresh profile data after successful update
        await fetchProfile()
        await refreshUser()

        toast({
          title: "Profile Updated",
          description: "Your profile has been successfully updated.",
        })

        // If profile is now fully complete, redirect back to dashboard
        if (completionPercentage === 100) {
          router.push("/creator-dashboard")
        }
      } else {
        toast({
          title: "Update Failed",
          description: result.error || "Failed to update profile.",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('💥 Profile update error:', error)
      toast({
        title: "Update Failed",
        description: "An error occurred while updating your profile.",
        variant: "destructive"
      })
    }
  }

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setUploadingAvatar(true)

      const formData = new FormData()
      formData.append('file', file)

      const response = await userServiceClient.upload<{ data: { profile_image_url: string } }>(
        '/api/v1/auth/profile-image',
        formData
      )

      if (response.success && response.data?.data?.profile_image_url) {
        const url = response.data.data.profile_image_url

        // Update local state so UI refreshes immediately
        setProfileData(prev => ({
          ...prev,
          avatar_url: url,
        }))

        // Refresh both profile and global auth state
        await fetchProfile()
        await refreshUser()

        toast({
          title: 'Profile Picture Updated',
          description: 'Your new profile picture has been uploaded.',
        })
      } else {
        toast({
          title: 'Upload Failed',
          description: response.error || 'Failed to upload avatar.',
          variant: 'destructive',
        })
      }
    } catch (error: any) {
      toast({
        title: 'Upload Failed',
        description: error.message || 'Failed to upload avatar.',
        variant: 'destructive',
      })
    } finally {
      setUploadingAvatar(false)
    }
  }

  const toggleSecondaryNiche = (niche: string) => {
    setProfileData(prev => ({
      ...prev,
      secondary_niches: prev.secondary_niches.includes(niche)
        ? prev.secondary_niches.filter(n => n !== niche)
        : [...prev.secondary_niches, niche]
    }))
  }

  const toggleContentStyle = (style: string) => {
    setProfileData(prev => ({
      ...prev,
      content_style: prev.content_style.includes(style)
        ? prev.content_style.filter(s => s !== style)
        : [...prev.content_style, style]
    }))
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <CreatorSidebar 
        isMobileOpen={isMobileSidebarOpen} 
        onMobileClose={() => setIsMobileSidebarOpen(false)} 
      />
      <div className="lg:ml-60 min-h-screen">
        <CreatorHeader onMobileMenuToggle={() => setIsMobileSidebarOpen(true)} />

        <div className="p-6 space-y-6">
          {/* Page Header */}
          <div className="space-y-4">
            <div>
              <h1 className="text-3xl font-bold">Complete Your Profile</h1>
              <p className="text-gray-400">Fill in your information to start earning with campaigns</p>
            </div>

            {/* Loading States */}
            {(profileLoading || demographicsLoading) && (
              <div className="flex items-center justify-center h-32">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                <p className="text-gray-400 ml-4">Loading profile data...</p>
              </div>
            )}

            {/* Error States */}
            {profileError && (
              <div className="mb-6 bg-red-900/20 border border-red-600/30 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-red-500 font-medium">Error Loading Profile</p>
                  <p className="text-red-400/80 text-sm">{profileError}</p>
                </div>
              </div>
            )}

            {demographicsError && (
              <div className="mb-6 bg-red-900/20 border border-red-600/30 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-red-500 font-medium">Error Loading Demographics</p>
                  <p className="text-red-400/80 text-sm">{demographicsError}</p>
                </div>
              </div>
            )}

            {/* Profile Completion Progress */}
            <Card className="bg-gradient-to-r from-purple-900/20 to-purple-600/20 border-purple-600/30">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-purple-400">{completionPercentage}% Profile Complete</h3>
                    <p className="text-gray-300">{incompleteItems} items left to complete</p>
                  </div>
                  <Button 
                    onClick={handleSaveProfile}
                    disabled={profileUpdating}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {profileUpdating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      "Save Profile"
                    )}
                  </Button>
                </div>
                <Progress value={completionPercentage} className="h-3 bg-gray-800">
                  <div
                    className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all"
                    style={{ width: `${completionPercentage}%` }}
                  />
                </Progress>
                <p className="text-sm text-gray-400 mt-2">Complete your profile to apply for premium campaigns</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Profile Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Avatar Upload */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Camera className="h-5 w-5" />
                    Profile Picture
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-6">
                    <div className="relative">
                      <div className="h-24 w-24 rounded-full bg-gray-800 flex items-center justify-center overflow-hidden">
                        {profileData.avatar_url ? (
                          <img 
                            src={profileData.avatar_url} 
                            alt="Avatar" 
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <Camera className="h-8 w-8 text-gray-400" />
                        )}
                      </div>
                      {uploadingAvatar && (
                        <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center">
                          <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="avatar-upload" className="cursor-pointer">
                        <div className="flex items-center gap-2 text-purple-400 hover:text-purple-300">
                          <Upload className="h-4 w-4" />
                          Upload new photo
                        </div>
                      </Label>
                      <Input
                        id="avatar-upload"
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleAvatarUpload}
                        disabled={uploadingAvatar}
                      />
                      <p className="text-sm text-gray-400 mt-1">JPG, PNG or GIF. Max 5MB.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Basic Information */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Basic Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        value={profileData.username}
                        onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                        placeholder="@username"
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">Email Address</Label>
                      <div className="flex items-center gap-2">
                        <Input id="email" value={profileData.email} className="bg-gray-800 border-gray-700" disabled />
                        <Badge variant="secondary" className="bg-green-600/20 text-green-400">
                          Verified
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="first_name">First Name</Label>
                      <Input
                        id="first_name"
                        value={profileData.first_name}
                        onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <Label htmlFor="last_name">Last Name</Label>
                      <Input
                        id="last_name"
                        value={profileData.last_name}
                        onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                        placeholder="Doe"
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="gender">Gender</Label>
                      <Select 
                        value={profileData.gender} 
                        onValueChange={(value) => setProfileData({ ...profileData, gender: value })}
                      >
                        <SelectTrigger className="bg-gray-800 border-gray-700">
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="FEMALE">Female</SelectItem>
                          <SelectItem value="MALE">Male</SelectItem>
                          <SelectItem value="NON_BINARY">Non-binary</SelectItem>
                          <SelectItem value="PREFER_NOT_TO_SAY">Prefer not to say</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      value={profileData.bio}
                      onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                      className="bg-gray-800 border-gray-700"
                      placeholder="Tell brands about yourself..."
                      rows={4}
                    />
                  </div>
                  <div className="text-sm text-gray-400 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Member since March 2025
                  </div>
                </CardContent>
              </Card>

              {/* Location & Shipping */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5" />
                    Location & Shipping
                    {!profileData.address_line1 && (
                      <Badge variant="destructive" className="ml-2">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Required
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="address_line1">Street Address</Label>
                    <Input
                      id="address_line1"
                      placeholder="123 Main St"
                      value={profileData.address_line1}
                      onChange={(e) => setProfileData({ ...profileData, address_line1: e.target.value })}
                      className="bg-gray-800 border-gray-700"
                    />
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <Label htmlFor="city">City</Label>
                      <Input
                        id="city"
                        placeholder="Los Angeles"
                        value={profileData.city}
                        onChange={(e) => setProfileData({ ...profileData, city: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                      />
                    </div>
                    <div>
                      <Label htmlFor="state">State</Label>
                      <Input
                        id="state"
                        placeholder="CA"
                        value={profileData.state}
                        onChange={(e) => setProfileData({ ...profileData, state: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                      />
                    </div>
                    <div>
                      <Label htmlFor="postal_code">ZIP Code</Label>
                      <Input
                        id="postal_code"
                        placeholder="90210"
                        value={profileData.postal_code}
                        onChange={(e) => setProfileData({ ...profileData, postal_code: e.target.value })}
                        className="bg-gray-800 border-gray-700"
                      />
                    </div>
                    <div>
                      <Label htmlFor="country">Country</Label>
                      <Select 
                        value={profileData.country}
                        onValueChange={(value) => setProfileData({ ...profileData, country: value })}
                      >
                        <SelectTrigger className="bg-gray-800 border-gray-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="United States">United States</SelectItem>
                          <SelectItem value="Canada">Canada</SelectItem>
                          <SelectItem value="United Kingdom">United Kingdom</SelectItem>
                          <SelectItem value="Australia">Australia</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400">Required for shipping product samples</p>
                </CardContent>
              </Card>

              {/* Social Media Handles */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LinkIcon className="h-5 w-5" />
                    Social Media Handles
                    {!profileData.tiktok_handle && (
                      <Badge variant="destructive" className="ml-2">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        TikTok Required
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="tiktok_handle">TikTok Username</Label>
                    <Input
                      id="tiktok_handle"
                      value={profileData.tiktok_handle}
                      onChange={(e) => setProfileData({ ...profileData, tiktok_handle: e.target.value })}
                      className="bg-gray-800 border-gray-700"
                      placeholder="@yourtiktok"
                    />
                    <p className="text-sm text-gray-400 mt-1">Required for campaign participation</p>
                  </div>
                  <div>
                    <Label htmlFor="instagram_handle">Instagram Username</Label>
                    <Input
                      id="instagram_handle"
                      value={profileData.instagram_handle}
                      onChange={(e) => setProfileData({ ...profileData, instagram_handle: e.target.value })}
                      className="bg-gray-800 border-gray-700"
                      placeholder="@yourinstagram"
                    />
                  </div>
                  <div>
                    <Label htmlFor="discord_handle">Discord Username</Label>
                    <Input
                      id="discord_handle"
                      value={profileData.discord_handle}
                      onChange={(e) => setProfileData({ ...profileData, discord_handle: e.target.value })}
                      className="bg-gray-800 border-gray-700"
                      placeholder="username#1234"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Content Niche Preferences */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Content Niche Preferences
                    {!profileData.primary_niche && (
                      <Badge variant="destructive" className="ml-2">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Required
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="primary_niche">Primary Niche</Label>
                    <Select 
                      value={profileData.primary_niche}
                      onValueChange={(value) => setProfileData({ ...profileData, primary_niche: value })}
                    >
                      <SelectTrigger className="bg-gray-800 border-gray-700">
                        <SelectValue placeholder="Select your primary niche" />
                      </SelectTrigger>
                      <SelectContent>
                        {NICHES.map(niche => (
                          <SelectItem key={niche} value={niche}>{niche}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Secondary Niches</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {NICHES.filter(n => n !== profileData.primary_niche).map((niche) => (
                        <Badge 
                          key={niche} 
                          variant={profileData.secondary_niches.includes(niche) ? "default" : "outline"}
                          className={profileData.secondary_niches.includes(niche) 
                            ? "bg-purple-600/20 text-purple-400 cursor-pointer" 
                            : "cursor-pointer hover:bg-gray-800"
                          }
                          onClick={() => toggleSecondaryNiche(niche)}
                        >
                          {niche}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <Label>Content Style</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {CONTENT_STYLES.map((style) => (
                        <Badge 
                          key={style} 
                          variant={profileData.content_style.includes(style) ? "default" : "outline"}
                          className={profileData.content_style.includes(style) 
                            ? "bg-purple-600/20 text-purple-400 cursor-pointer" 
                            : "cursor-pointer hover:bg-gray-800"
                          }
                          onClick={() => toggleContentStyle(style)}
                        >
                          {style}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Audience Demographics */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Audience Demographics
                    {!profileData.audienceDemographics && (
                      <Badge variant="destructive" className="ml-2">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Required
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-sm font-medium">Gender Distribution</Label>
                    <div className="space-y-2 mt-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Female</span>
                        <span className="text-sm">{audienceData.gender.female}%</span>
                      </div>
                      <Progress value={audienceData.gender.female} className="h-2" />
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Male</span>
                        <span className="text-sm">{audienceData.gender.male}%</span>
                      </div>
                      <Progress value={audienceData.gender.male} className="h-2" />
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Age Distribution</Label>
                    <div className="grid grid-cols-2 gap-4 mt-2">
                      {Object.entries(audienceData.age).map(([range, percentage]) => (
                        <div key={range} className="text-center p-3 bg-gray-800/50 rounded-lg">
                          <div className="text-lg font-semibold">{percentage}%</div>
                          <div className="text-sm text-gray-400">{range}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Top Locations</Label>
                    <p className="text-sm text-gray-300 mt-1">{audienceData.locations}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Total Audience Size</Label>
                    <p className="text-lg font-semibold text-purple-400">{performanceMetrics.followers} followers</p>
                  </div>
                </CardContent>
              </Card>

              {/* Notification Preferences */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Notification Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>SMS Notifications</Label>
                        <p className="text-sm text-gray-400">Receive text messages for urgent updates</p>
                      </div>
                      <Switch
                        checked={notifications.sms}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, sms: checked })}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Email Notifications</Label>
                        <p className="text-sm text-gray-400">Receive email updates and summaries</p>
                      </div>
                      <Switch
                        checked={notifications.email}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, email: checked })}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>In-app Notifications</Label>
                        <p className="text-sm text-gray-400">Show notifications within the app</p>
                      </div>
                      <Switch
                        checked={notifications.inApp}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, inApp: checked })}
                      />
                    </div>
                  </div>

                  <Separator className="bg-gray-700" />

                  <div className="space-y-4">
                    <Label className="text-sm font-medium">Notification Types</Label>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Campaign deadlines</span>
                        <Switch
                          checked={notifications.campaigns}
                          onCheckedChange={(checked) => setNotifications({ ...notifications, campaigns: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Payment confirmations</span>
                        <Switch
                          checked={notifications.payments}
                          onCheckedChange={(checked) => setNotifications({ ...notifications, payments: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">New opportunities</span>
                        <Switch
                          checked={notifications.opportunities}
                          onCheckedChange={(checked) => setNotifications({ ...notifications, opportunities: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Performance updates</span>
                        <Switch
                          checked={notifications.performance}
                          onCheckedChange={(checked) => setNotifications({ ...notifications, performance: checked })}
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Account Settings */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Account Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Password</Label>
                        <p className="text-sm text-gray-400">Last changed 3 months ago</p>
                      </div>
                      <Button variant="outline" size="sm">
                        Change Password
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Two-Factor Authentication</Label>
                        <p className="text-sm text-gray-400">Add an extra layer of security</p>
                      </div>
                      <Button variant="outline" size="sm">
                        Enable 2FA
                      </Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Data Export</Label>
                        <p className="text-sm text-gray-400">Download your account data</p>
                      </div>
                      <Button variant="outline" size="sm">
                        Download Data
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar Content */}
            <div className="space-y-6">
              {/* Profile Completion Checklist */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    Profile Completion
                    {(profileLoading || demographicsLoading) && (
                      <Badge variant="secondary" className="ml-2">
                        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        Loading...
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(profileLoading || demographicsLoading) ? (
                    <div className="space-y-3">
                      {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                        <div key={i} className="flex items-start gap-3">
                          <div className="h-5 w-5 bg-gray-800 rounded animate-pulse mt-0.5"></div>
                          <div className="flex-1">
                            <div className="h-4 bg-gray-800 rounded animate-pulse mb-1"></div>
                            <div className="h-3 bg-gray-800 rounded animate-pulse w-32"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    completionItems.map((item) => (
                      <div key={item.name} className="flex items-start gap-3">
                        {item.completed ? (
                          <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-orange-400 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{item.name}</div>
                          <div className="text-xs text-gray-400">{item.description}</div>
                          {!item.completed && (
                            <Button size="sm" className="mt-2 bg-purple-600 hover:bg-purple-700">
                              Complete
                            </Button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              {/* Performance Overview */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Performance Overview
                    {performanceLoading && (
                      <Badge variant="secondary" className="ml-2">
                        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        Loading...
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {performanceLoading ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="h-8 bg-gray-800 rounded animate-pulse"></div>
                          <div className="text-xs text-gray-400 mt-1">Total GMV</div>
                        </div>
                        <div className="text-center">
                          <div className="h-8 bg-gray-800 rounded animate-pulse"></div>
                          <div className="text-xs text-gray-400 mt-1">Consistency</div>
                        </div>
                        <div className="text-center">
                          <div className="h-8 bg-gray-800 rounded animate-pulse"></div>
                          <div className="text-xs text-gray-400 mt-1">Avg Rating</div>
                        </div>
                        <div className="text-center">
                          <div className="h-8 bg-gray-800 rounded animate-pulse"></div>
                          <div className="text-xs text-gray-400 mt-1">Campaigns</div>
                        </div>
                      </div>
                    </div>
                  ) : performanceError ? (
                    <div className="text-center py-4">
                      <AlertCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-400">Failed to load performance data</p>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="mt-2"
                        onClick={fetchPerformance}
                      >
                        Retry
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">{performanceMetrics.totalGMV}</div>
                        <div className="text-xs text-gray-400">Total GMV</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">{performanceMetrics.consistency}</div>
                        <div className="text-xs text-gray-400">Consistency</div>
                      </div>
                      <div className="text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="text-lg font-bold">{performanceMetrics.rating}</span>
                        </div>
                        <div className="text-xs text-gray-400">Avg Rating</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold">{performanceMetrics.campaignsCompleted}</div>
                        <div className="text-xs text-gray-400">Campaigns</div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Badges */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Badges & Achievements
                    {performanceLoading && (
                      <Badge variant="secondary" className="ml-2">
                        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                        Loading...
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {performanceLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-gray-800 animate-pulse"></div>
                          <div className="flex-1">
                            <div className="h-4 bg-gray-800 rounded animate-pulse mb-1"></div>
                            <div className="h-3 bg-gray-800 rounded animate-pulse w-16"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    badges.map((badge) => (
                      <div key={badge.name} className="flex items-center gap-3">
                        <div className={`h-8 w-8 rounded-full ${badge.color} flex items-center justify-center`}>
                          <Award className="h-4 w-4 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-sm">{badge.name}</div>
                          {badge.earned ? (
                            <Badge variant="secondary" className="bg-green-600/20 text-green-400 text-xs">
                              Earned
                            </Badge>
                          ) : (
                            <div className="text-xs text-gray-400">{badge.progress}% progress</div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>

              {/* Integration Status */}
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Integration Status
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Connect your accounts to unlock more campaign opportunities and automated features
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">TikTok Account</span>
                        <span className="text-xs text-gray-400">Connect your TikTok account</span>
                      </div>
                      <Badge variant="outline" className="text-gray-400 border-gray-500">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Connected
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" className="w-full bg-transparent border-gray-600 text-gray-300 hover:bg-gray-800">
                      Connect TikTok Account
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Discord Integration</span>
                        <span className="text-xs text-gray-400">Join creator communities</span>
                      </div>
                      <Badge variant="outline" className="text-gray-400 border-gray-500">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Connected
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" className="w-full bg-transparent border-gray-600 text-gray-300 hover:bg-gray-800">
                      Connect Discord
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">SMS Notifications</span>
                        <span className="text-xs text-gray-400">Get campaign updates</span>
                      </div>
                      <Badge variant="outline" className="text-gray-400 border-gray-500">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Connected
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" className="w-full bg-transparent border-gray-600 text-gray-300 hover:bg-gray-800">
                      Enable SMS
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Payment Method</span>
                        <span className="text-xs text-gray-400">Receive campaign payments</span>
                      </div>
                      <Badge variant="outline" className="text-gray-400 border-gray-500">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Connected
                      </Badge>
                    </div>
                    <Button size="sm" variant="outline" className="w-full bg-transparent border-gray-600 text-gray-300 hover:bg-gray-800">
                      Add Payment Method
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 