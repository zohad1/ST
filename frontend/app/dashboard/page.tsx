"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { useAuth } from "@/hooks/useAuth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AlertTriangle, LogOut } from "lucide-react"

export default function FallbackDashboardPage() {
  const { user, logout, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    console.log("🔍 [FallbackDashboard] Auth state:", { user, isAuthenticated })
    console.log("🔍 [FallbackDashboard] User role:", user?.role)

    // Add a small delay to let auth state stabilize
    const timer = setTimeout(() => {
      // Handle authentication redirect
      if (!isAuthenticated) {
        console.log("🔄 [FallbackDashboard] Not authenticated, redirecting to login")
        router.push("/auth/login")
        return
      }

      // If user has a role, redirect to the appropriate dashboard
      if (user?.role) {
        console.log("🔄 [FallbackDashboard] User has role, redirecting to:", user.role)
        switch (user.role) {
          case "creator":
            router.push("/creator-dashboard")
            break
          case "agency":
            router.push("/agency-dashboard")
            break
          case "brand":
            router.push("/client-dashboard")
            break
          default:
            console.log("🔄 [FallbackDashboard] Unknown role, staying on fallback dashboard")
            break
        }
      } else {
        console.log("🔍 [FallbackDashboard] No role found, staying on fallback dashboard")
      }
    }, 200) // Small delay to let auth state stabilize

    return () => clearTimeout(timer)
  }, [user, router, isAuthenticated])

  // Show loading while redirecting
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
      <Card className="bg-gray-900 border-gray-800 max-w-md w-full">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <AlertTriangle className="h-12 w-12 text-yellow-400" />
          </div>
          <CardTitle className="text-xl">Dashboard Access Issue</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-gray-400">
            <p>We're having trouble determining your account type.</p>
            <p className="mt-2">Please contact support or try logging in again.</p>
          </div>
          
          {user && (
            <div className="bg-gray-800 rounded p-3 text-sm">
              <p><strong>User ID:</strong> {user.id}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Role:</strong> {user.role || "Not specified"}</p>
            </div>
          )}
          
          <div className="flex gap-2">
            <Button 
              onClick={() => window.location.reload()} 
              className="flex-1 bg-purple-600 hover:bg-purple-700"
            >
              Refresh Page
            </Button>
            <Button 
              onClick={logout} 
              variant="outline"
              className="flex-1 border-gray-700 hover:bg-gray-800"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Log Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 