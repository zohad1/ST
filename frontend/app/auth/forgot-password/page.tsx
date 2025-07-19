"use client"

import type React from "react"

import { useState, useEffect, Suspense } from "react"
import Link from "next/link"
import Image from "next/image"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Mail, ArrowLeft, Send, CheckCircle, Shield, Lock, Eye, EyeOff, AlertCircle } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToast } from "@/hooks/use-toast"

type ForgotPasswordStep = "email" | "reset" | "success"

// Animated background component (consistent with auth pages)
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0">
        <div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "4s" }}
        />
        <div
          className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-400/8 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "6s", animationDelay: "2s" }}
        />
        <div
          className="absolute top-1/2 left-1/2 w-72 h-72 bg-purple-600/6 rounded-full blur-3xl animate-pulse"
          style={{ animationDuration: "8s", animationDelay: "4s" }}
        />
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-purple-400/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>
    </div>
  )
}

// Password strength indicator (reused from auth page)
function PasswordStrength({ password }: { password: string }) {
  const getStrength = (pass: string) => {
    let score = 0
    if (pass.length >= 8) score += 25
    if (/[A-Z]/.test(pass)) score += 25
    if (/[0-9]/.test(pass)) score += 25
    if (/[^A-Za-z0-9]/.test(pass)) score += 25
    return score
  }

  const strength = getStrength(password)
  const getStrengthText = () => {
    if (strength < 50) return "Weak"
    if (strength < 75) return "Medium"
    return "Strong"
  }

  const getStrengthColor = () => {
    if (strength < 50) return "bg-red-500"
    if (strength < 75) return "bg-yellow-500"
    return "bg-green-500"
  }

  if (!password) return null

  return (
    <div className="mt-2 space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">Password strength</span>
        <span
          className={`font-medium ${
            strength < 50 ? "text-red-400" : strength < 75 ? "text-yellow-400" : "text-green-400"
          }`}
        >
          {getStrengthText()}
        </span>
      </div>
      <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full transition-all duration-300 ${getStrengthColor()}`} style={{ width: `${strength}%` }} />
      </div>
    </div>
  )
}

function ForgotPasswordContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { forgotPassword, resetPassword } = useAuth()
  const { toast } = useToast()
  
  const [mounted, setMounted] = useState(false)
  const [step, setStep] = useState<ForgotPasswordStep>("email")
  const [email, setEmail] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmNewPassword, setConfirmNewPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [emailError, setEmailError] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false)

  // Get token from URL for password reset
  const token = searchParams.get('token')
  const emailFromUrl = searchParams.get('email')

  useEffect(() => {
    setMounted(true)
    
    // If token is present, go directly to reset step
    if (token && emailFromUrl) {
      setEmail(emailFromUrl)
      setStep("reset")
    }
  }, [token, emailFromUrl])

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailError("")

    if (!email) {
      setEmailError("Email is required")
      return
    }

    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      return
    }

    setIsLoading(true)

    try {
      const result = await forgotPassword({ email })
      
      if (result.success) {
        toast({
          title: "Email Sent!",
          description: "If an account with this email exists, a password reset link has been sent.",
        })
        setStep("success")
      } else {
        setEmailError(result.error || "Failed to send reset email")
        toast({
          title: "Error",
          description: result.error || "Failed to send password reset email. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error: any) {
      setEmailError("An unexpected error occurred")
      toast({
        title: "Error",
        description: "Failed to send password reset email. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError("")

    if (!newPassword || !confirmNewPassword) {
      setPasswordError("Both password fields are required.")
      return
    }

    if (newPassword.length < 8) {
      setPasswordError("Password must be at least 8 characters long.")
      return
    }

    if (newPassword !== confirmNewPassword) {
      setPasswordError("Passwords do not match.")
      return
    }

    if (!token) {
      setPasswordError("Invalid reset token. Please request a new password reset.")
      return
    }

    setIsLoading(true)

    try {
      const result = await resetPassword({
        token,
        new_password: newPassword
      })
      
      if (result.success) {
        toast({
          title: "Password Reset!",
          description: "Your password has been successfully reset. You can now log in with your new password.",
        })
        setStep("success")
      } else {
        setPasswordError(result.error || "Failed to reset password")
        toast({
          title: "Reset Failed",
          description: result.error || "Failed to reset password. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error: any) {
      setPasswordError("An unexpected error occurred")
      toast({
        title: "Error",
        description: "Failed to reset password. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleBackToLogin = () => {
    router.push("/auth/login")
  }

  const handleTryAgain = () => {
    setStep("email")
    setEmail("")
    setNewPassword("")
    setConfirmNewPassword("")
    setEmailError("")
    setPasswordError("")
  }

  const toggleNewPasswordVisibility = () => setShowNewPassword(!showNewPassword)
  const toggleConfirmNewPasswordVisibility = () => setShowConfirmNewPassword(!showConfirmNewPassword)

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
        {/* Logo */}
        <Link href="/" className="mb-8 animate-fade-in">
          <Image src="/logo.png" alt="LaunchPAID Logo" width={180} height={40} className="h-10 w-auto" />
        </Link>

        {/* Back to Login Button */}
        {step !== "success" && (
          <Button
            variant="ghost"
            onClick={handleBackToLogin}
            className="absolute top-8 left-8 text-gray-400 hover:text-white transition-colors duration-200 animate-fade-in"
            style={{ animationDelay: "0.1s" }}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Login
          </Button>
        )}

        {/* Main Forgot Password Container */}
        <div className="w-full max-w-md animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          {step === "email" && (
            /* Request Email Form */
            <Card className="bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl shadow-2xl shadow-purple-500/10">
              <CardHeader className="text-center space-y-2">
                <div className="flex justify-center mb-4">
                  <div className="h-16 w-16 bg-purple-600/20 rounded-full flex items-center justify-center animate-scale-in">
                    <Mail className="h-8 w-8 text-purple-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl font-bold">Forgot Password?</CardTitle>
                <CardDescription className="text-gray-400">
                  No worries! Enter your email address and we'll send you a link to reset your password.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  {/* Email Field */}
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm font-medium">
                      Email Address
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                        disabled={isLoading}
                      />
                    </div>
                    {emailError && (
                      <p className="text-red-400 text-sm flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {emailError}
                      </p>
                    )}
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-medium transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/25 rounded-xl"
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        Sending...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Send className="h-4 w-4" />
                        Send Reset Link
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {step === "reset" && (
            /* Reset Password Form */
            <Card className="bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl shadow-2xl shadow-purple-500/10">
              <CardHeader className="text-center space-y-2">
                <div className="flex justify-center mb-4">
                  <div className="h-16 w-16 bg-red-600/20 rounded-full flex items-center justify-center animate-scale-in">
                    <Shield className="h-8 w-8 text-red-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl font-bold">Reset Your Password</CardTitle>
                <CardDescription className="text-gray-400">
                  Enter your new password below. Make sure it's secure and memorable.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <form onSubmit={handlePasswordResetSubmit} className="space-y-4">
                  {/* New Password Field */}
                  <div className="space-y-2">
                    <Label htmlFor="new-password" className="text-sm font-medium">
                      New Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="new-password"
                        type={showNewPassword ? "text" : "password"}
                        placeholder="Enter your new password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="pl-10 pr-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                        disabled={isLoading}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={toggleNewPasswordVisibility}
                        className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-gray-700/50"
                      >
                        {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    <PasswordStrength password={newPassword} />
                  </div>

                  {/* Confirm New Password Field */}
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password" className="text-sm font-medium">
                      Confirm New Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="confirm-password"
                        type={showConfirmNewPassword ? "text" : "password"}
                        placeholder="Confirm your new password"
                        value={confirmNewPassword}
                        onChange={(e) => setConfirmNewPassword(e.target.value)}
                        className="pl-10 pr-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                        disabled={isLoading}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={toggleConfirmNewPasswordVisibility}
                        className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-gray-700/50"
                      >
                        {showConfirmNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  {passwordError && (
                    <p className="text-red-400 text-sm flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {passwordError}
                    </p>
                  )}

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-12 bg-red-600 hover:bg-red-700 text-white font-medium transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-red-500/25 rounded-xl"
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        Resetting...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        Reset Password
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {step === "success" && (
            /* Success State */
            <Card className="bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl shadow-2xl shadow-green-500/10">
              <CardHeader className="text-center space-y-2">
                <div className="flex justify-center mb-4">
                  <div className="h-16 w-16 bg-green-600/20 rounded-full flex items-center justify-center animate-scale-in">
                    <CheckCircle className="h-8 w-8 text-green-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl font-bold">Success!</CardTitle>
                <CardDescription className="text-gray-400">
                  Your password has been reset successfully. You can now log in with your new password.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <div className="text-center space-y-4">
                  <p className="text-gray-300">
                    You can now return to the login page and sign in with your new password.
                  </p>
                  
                <div className="flex flex-col gap-3">
                  <Button
                    onClick={handleBackToLogin}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/25 rounded-xl"
                  >
                    Back to Login
                  </Button>
                    
                    <Button 
                      variant="outline"
                      onClick={handleTryAgain}
                      className="w-full border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white transition-all duration-200 rounded-xl"
                    >
                      Reset Another Password
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ForgotPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <ForgotPasswordContent />
    </Suspense>
  )
}
