"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Eye, EyeOff, Mail, Lock, User, Users, Building, Shield, Check, AlertCircle } from "lucide-react"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { useToast } from "@/hooks/use-toast"

type Role = "creator" | "agency" | "brand"
type FormType = "login" | "signup"

// Animated background component
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

// Password strength indicator
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

export default function AuthPage() {
  const pathname = usePathname()
  const router = useRouter()
  const { toast } = useToast()

  // Use the real auth hook
  const { login, register, isLoading: authLoading, error: authError, clearError, user, isAuthenticated } = useAuth()

  const getInitialFormType = (): FormType => {
    if (pathname === "/auth/login") return "login"
    if (pathname === "/auth/signup") return "signup"
    return "signup" // Default to signup if path is just /auth or unknown
  }

  const [formType, setFormType] = useState<FormType>(getInitialFormType())
  const [selectedRole, setSelectedRole] = useState<Role>("creator")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [loginSuccess, setLoginSuccess] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    fullName: "",
    tiktokUsername: "",
    rememberMe: false,
    acceptTerms: false,
  })

  useEffect(() => {
    setMounted(true)
    // Update formType if the pathname changes
    const currentFormType = getInitialFormType()
    if (currentFormType !== formType) {
      setFormType(currentFormType)
    }
  }, [pathname, formType])

  // Redirect already authenticated users to their dashboard
  useEffect(() => {
    if (mounted && isAuthenticated && user && !authLoading && !submitError && loginSuccess) {
      console.log("🔄 [AuthPage] User already authenticated, redirecting to dashboard...")
      console.log("🔍 [AuthPage] User:", user)
      console.log("🔍 [AuthPage] User role:", user.role)
      
      // Add longer delay to prevent conflicts with login redirect
      const timer = setTimeout(() => {
        const getDashboardUrl = (role: string): string => {
          switch (role) {
            case "creator":
              return "/creator-dashboard"
            case "agency":
              return "/agency-dashboard"
            case "brand":
              return "/client-dashboard"
            default:
              return "/"
          }
        }
        
        const dashboardUrl = getDashboardUrl(user.role || "")
        console.log("🔄 [AuthPage] Redirecting to:", dashboardUrl)
        router.push(dashboardUrl)
      }, 1000) // Increased delay to prevent conflicts

      return () => clearTimeout(timer)
    }
  }, [mounted, isAuthenticated, user, router, authLoading, submitError, loginSuccess])

  const handleRoleChange = (value: string) => {
    setSelectedRole(value as Role)
  }

  const togglePasswordVisibility = () => setShowPassword(!showPassword)
  const toggleConfirmPasswordVisibility = () => setShowConfirmPassword(!showConfirmPassword)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError(null)
    setLoginSuccess(false)
    clearError()

    // Validation
    if (!formData.email || !formData.password) {
      setSubmitError("Please fill in all required fields")
      return
    }

    if (formType === "signup") {
      if (!formData.fullName) {
        setSubmitError("Full name is required")
        return
      }
      if (formData.password !== formData.confirmPassword) {
        setSubmitError("Passwords do not match")
        return
      }
      if (!formData.acceptTerms) {
        setSubmitError("Please accept the terms and conditions")
        return
      }
    }

    try {
      if (formType === "login") {
        const result = await login({
          email: formData.email,
          password: formData.password,
        })
        
        if (!result.success) {
          setSubmitError(result.error || "Login failed")
          setLoginSuccess(false)
          return
        }
        
        // Clear any previous errors and set success flag
        setSubmitError(null)
        setLoginSuccess(true)
        
        // Show success message briefly before redirect
        toast({
          title: "Login Successful!",
          description: "Redirecting to your dashboard...",
        })
        
        // Let the useEffect handle the redirect after state updates
        // The useAuth hook will update the authentication state
      } else {
        // Parse full name into first and last name
        const nameParts = formData.fullName.trim().split(' ')
        const firstName = nameParts[0] || ''
        const lastName = nameParts.slice(1).join(' ') || ''

        // Generate a valid username from email
        const generateUsername = (email: string) => {
          const prefix = email.split('@')[0]
          // Remove invalid characters and ensure it matches the backend pattern: ^[a-zA-Z0-9_-]+$
          return prefix.replace(/[^a-zA-Z0-9_-]/g, '').toLowerCase()
        }

        const result = await register({
          email: formData.email,
          password: formData.password,
          firstName,
          lastName,
          username: generateUsername(formData.email),
          role: selectedRole,
        })

        if (result.success) {
          if (result.requires_verification) {
            router.push(`/auth/signup/verification?email=${encodeURIComponent(formData.email)}`)
          }
          // useAuth hook will handle redirect automatically for successful registration
        } else {
          setSubmitError(result.error || "Registration failed")
        }
      }
    } catch (error: any) {
      setSubmitError(error.message || "An unexpected error occurred")
    }
  }

  const updateFormData = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleTabChange = (value: string) => {
    const newFormType = value as FormType
    setFormType(newFormType)
    // Update URL without full page reload
    router.push(`/auth/${newFormType}`, { scroll: false })
  }

  const getRoleContent = () => {
    switch (selectedRole) {
      case "creator":
        return "Join thousands of creators earning with brands"
      case "agency":
        return "Manage campaigns and scale your creator network"
      case "brand":
        return "Connect with top-performing creators"
      default:
        return "Join LaunchPaid and start growing"
    }
  }

  if (!mounted) return null

  // Show loading while redirecting authenticated users
  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen bg-black text-white relative overflow-hidden flex items-center justify-center">
        <AnimatedBackground />
        <div className="relative z-10 text-center">
          <Image src="/logo.png" alt="LaunchPAID Logo" width={180} height={40} className="h-10 w-auto mb-4 mx-auto" />
          <p className="text-gray-400">Redirecting to your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
        {/* Logo */}
        <Link href="/" className="mb-8 animate-fade-in">
          <Image 
            src="/logo.png" 
            alt="LaunchPAID Logo" 
            width={180} 
            height={40} 
            className="h-10 w-auto" 
            style={{ width: 'auto', height: '40px' }}
          />
        </Link>

        {/* Main Auth Container */}
        <div className="w-full max-w-md animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          <Tabs
            defaultValue="signup"
            value={formType}
            onValueChange={handleTabChange} // Use handleTabChange
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2 bg-gray-800/50 border border-gray-700/50 backdrop-blur-sm">
              <TabsTrigger
                value="signup"
                className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all duration-200"
              >
                Sign Up
              </TabsTrigger>
              <TabsTrigger
                value="login"
                className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all duration-200"
              >
                Log In
              </TabsTrigger>
            </TabsList>

            {/* Glassmorphism Card */}
            <Card className="bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl mt-1 shadow-2xl shadow-purple-500/10">
              <CardHeader className="text-center space-y-2">
                <CardTitle className="text-2xl font-bold">
                  {formType === "signup" ? "Create Your Account" : "Welcome Back!"}
                </CardTitle>
                <CardDescription className="text-gray-400">
                  {formType === "signup" ? "Create your account to get started" : "Log in to access your dashboard"}
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Social Login Section */}

                {/* Role Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">I am a...</Label>
                  <RadioGroup
                    defaultValue="creator"
                    value={selectedRole}
                    onValueChange={handleRoleChange}
                    className="grid grid-cols-3 gap-3"
                  >
                    {[
                      { value: "creator", label: "Creator", icon: <User className="h-4 w-4" /> },
                      { value: "agency", label: "Agency", icon: <Users className="h-4 w-4" /> },
                      { value: "brand", label: "Brand", icon: <Building className="h-4 w-4" /> },
                    ].map((role) => (
                      <Label
                        key={role.value}
                        htmlFor={`role-${role.value}-${formType}`}
                        className={`flex flex-col items-center justify-center p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:scale-[1.02]
                                ${
                                  selectedRole === role.value
                                    ? "bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-500/25"
                                    : "bg-gray-800/50 border-gray-700 hover:bg-gray-700/50 hover:border-gray-600"
                                }`}
                      >
                        <RadioGroupItem value={role.value} id={`role-${role.value}-${formType}`} className="sr-only" />
                        <span className="sr-only">{role.label}</span>
                        {role.icon}
                        <span className="text-xs mt-1">{role.label}</span>
                      </Label>
                    ))}
                  </RadioGroup>
                </div>

                {/* Form Fields */}
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Sign Up Specific Fields */}
                  {formType === "signup" && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="full-name" className="text-sm font-medium">
                          Full Name
                        </Label>
                        <div className="relative">
                          <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                          <Input
                            id="full-name"
                            placeholder="Your Name"
                            value={formData.fullName}
                            onChange={(e) => updateFormData("fullName", e.target.value)}
                            className="pl-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                          />
                        </div>
                      </div>

                      {selectedRole === "creator" && (
                        <div className="space-y-2">
                          <Label htmlFor="tiktok-username" className="text-sm font-medium">
                            TikTok Username
                          </Label>
                          <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">@</span>
                            <Input
                              id="tiktok-username"
                              placeholder="yourtiktok"
                              value={formData.tiktokUsername}
                              onChange={(e) => updateFormData("tiktokUsername", e.target.value)}
                              className="pl-8 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                            />
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* Email Field */}
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm font-medium">
                      Email
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={formData.email}
                        onChange={(e) => updateFormData("email", e.target.value)}
                        className="pl-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-sm font-medium">
                      Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={(e) => updateFormData("password", e.target.value)}
                        className="pl-10 pr-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 px-2 text-gray-400 hover:text-white"
                        onClick={togglePasswordVisibility}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    {formType === "signup" && <PasswordStrength password={formData.password} />}
                  </div>

                  {/* Confirm Password (Sign Up Only) */}
                  {formType === "signup" && (
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password" className="text-sm font-medium">
                        Confirm Password
                      </Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <Input
                          id="confirm-password"
                          type={showConfirmPassword ? "text" : "password"}
                          placeholder="••••••••"
                          value={formData.confirmPassword}
                          onChange={(e) => updateFormData("confirmPassword", e.target.value)}
                          className="pl-10 pr-10 bg-gray-800/50 border-gray-700 focus:border-purple-500 focus:ring-purple-500/20 transition-all duration-200"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 px-2 text-gray-400 hover:text-white"
                          onClick={toggleConfirmPasswordVisibility}
                        >
                          {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                        {formData.confirmPassword && (
                          <div className="absolute right-10 top-1/2 -translate-y-1/2">
                            {formData.password === formData.confirmPassword ? (
                              <Check className="h-4 w-4 text-green-400" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-red-400" />
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Error Display */}
                  {submitError && (
                    <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg animate-fade-in">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-red-400" />
                        <span className="text-sm text-red-400 font-medium">{submitError}</span>
                      </div>
                    </div>
                  )}

                  {/* Remember Me / Terms */}
                  <div className="space-y-3">
                    {formType === "login" ? (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="remember-me"
                            checked={formData.rememberMe}
                            onCheckedChange={(checked) => updateFormData("rememberMe", checked as boolean)}
                            className="border-gray-600 data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600"
                          />
                          <Label htmlFor="remember-me" className="text-sm text-gray-300">
                            Remember me
                          </Label>
                        </div>
                        <Link href="/auth/forgot-password" className="text-sm text-purple-400 hover:underline">
                          Forgot Password?
                        </Link>
                      </div>
                    ) : (
                      <div className="flex items-start space-x-2">
                        <Checkbox
                          id="accept-terms"
                          checked={formData.acceptTerms}
                          onCheckedChange={(checked) => updateFormData("acceptTerms", checked as boolean)}
                          className="border-gray-600 data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600 mt-0.5"
                        />
                        <Label htmlFor="accept-terms" className="text-sm text-gray-300 leading-relaxed">
                          I agree to the{" "}
                          <Link href="#" className="text-purple-400 hover:underline">
                            Terms of Service
                          </Link>{" "}
                          and{" "}
                          <Link href="#" className="text-purple-400 hover:underline">
                            Privacy Policy
                          </Link>
                        </Label>
                      </div>
                    )}
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={authLoading}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/25"
                  >
                    {authLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        {formType === "signup" ? "Creating Account..." : "Signing In..."}
                      </div>
                    ) : formType === "signup" ? (
                      "Create Account"
                    ) : (
                      "Sign In"
                    )}
                  </Button>
                </form>

                {/* Security Indicator */}
                <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
                  <Shield className="h-3 w-3" />
                  <span>Secure connection</span>
                </div>
              </CardContent>

              <CardFooter className="flex justify-center">
                <p className="text-sm text-gray-400">
                  {formType === "signup" ? (
                    <>
                      Already have an account?{" "}
                      <Button
                        variant="link"
                        className="p-0 h-auto text-purple-400 hover:text-purple-300"
                        onClick={() => handleTabChange("login")}
                      >
                        Sign In
                      </Button>
                    </>
                  ) : (
                    <>
                      Don&apos;t have an account?{" "}
                      <Button
                        variant="link"
                        className="p-0 h-auto text-purple-400 hover:text-purple-300"
                        onClick={() => handleTabChange("signup")}
                      >
                        Sign Up
                      </Button>
                    </>
                  )}
                </p>
              </CardFooter>
            </Card>
          </Tabs>
        </div>

        {/* Footer */}
        <p className="text-xs text-gray-600 mt-8 text-center animate-fade-in" style={{ animationDelay: "0.4s" }}>
          Powered by Novanex
        </p>
      </div>

      <style jsx global>{`
      @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      @keyframes fade-in-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .animate-fade-in {
        animation: fade-in 0.6s ease-out forwards;
      }

      .animate-fade-in-up {
        animation: fade-in-up 0.6s ease-out forwards;
      }
    `}</style>
    </div>
  )
}
