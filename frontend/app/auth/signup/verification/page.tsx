"use client"

import { useEffect, useState, Suspense } from "react"
import Link from "next/link"
import Image from "next/image"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { MailCheck, Loader2, ArrowRight, CheckCircle, AlertCircle } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useToast } from "@/hooks/use-toast"

// Animated background component (reused from auth page for consistency)
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

function VerificationContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { verifyEmail, resendVerification } = useAuth()
  const { toast } = useToast()
  
  const [mounted, setMounted] = useState(false)
  const [resending, setResending] = useState(false)
  const [resendSuccess, setResendSuccess] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error'>('pending')
  const [errorMessage, setErrorMessage] = useState<string>('')

  // Get token and email from URL
  const token = searchParams.get('token')
  const email = searchParams.get('email')

  useEffect(() => {
    setMounted(true)
    
    // Auto-verify if token is present
    if (token) {
      handleVerification()
    }
  }, [token])

  const handleVerification = async () => {
    if (!token) {
      setVerificationStatus('error')
      setErrorMessage('No verification token found')
      return
    }

    setVerifying(true)
    setVerificationStatus('pending')

    try {
      const result = await verifyEmail({ token })
      
      if (result.success) {
        setVerificationStatus('success')
        toast({
          title: "Email Verified!",
          description: "Your account has been successfully verified. Welcome to LaunchPAID!",
        })
        
        // Redirect to login after a short delay
        setTimeout(() => {
          router.push('/auth/login')
        }, 3000)
      } else {
        setVerificationStatus('error')
        setErrorMessage(result.error || 'Verification failed')
        toast({
          title: "Verification Failed",
          description: result.error || "Failed to verify your email. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error: any) {
      setVerificationStatus('error')
      setErrorMessage(error.message || 'Verification failed')
      toast({
        title: "Verification Failed",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      })
    } finally {
      setVerifying(false)
    }
  }

  const handleResendEmail = async () => {
    if (!email) {
      toast({
        title: "Error",
        description: "Email address not found. Please try signing up again.",
        variant: "destructive",
      })
      return
    }

    setResending(true)
    setResendSuccess(false)

    try {
      const result = await resendVerification(email)
      
      if (result.success) {
        setResendSuccess(true)
        toast({
          title: "Email Sent!",
          description: "A new verification email has been sent to your inbox.",
        })
      } else {
        toast({
          title: "Failed to Send Email",
          description: result.error || "Failed to resend verification email. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to resend verification email. Please try again.",
        variant: "destructive",
      })
    } finally {
      setResending(false)
    }
  }

  if (!mounted) return null

  // Show verification success state
  if (verificationStatus === 'success') {
    return (
      <div className="min-h-screen bg-black text-white relative overflow-hidden">
        <AnimatedBackground />

        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
          <Link href="/" className="mb-8 animate-fade-in">
            <Image src="/logo.png" alt="LaunchPAID Logo" width={180} height={40} className="h-10 w-auto" />
          </Link>

          <div className="w-full max-w-md bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl rounded-xl p-8 text-center shadow-2xl shadow-purple-500/10 animate-fade-in-up">
            <div className="flex justify-center mb-6">
              <div className="h-20 w-20 bg-green-600/20 rounded-full flex items-center justify-center animate-scale-in">
                <CheckCircle className="h-10 w-10 text-green-500 animate-bounce-in" />
              </div>
            </div>
            <h1 className="text-3xl font-bold mb-4 text-green-400">Email Verified!</h1>
            <p className="text-gray-300 mb-6">
              Your account has been successfully verified. Welcome to LaunchPAID!
            </p>
            <p className="text-sm text-gray-400 mb-6">
              Redirecting to login page...
            </p>
            <Link href="/auth/login">
              <Button className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-medium">
                Go to Login <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Show verification error state
  if (verificationStatus === 'error') {
    return (
      <div className="min-h-screen bg-black text-white relative overflow-hidden">
        <AnimatedBackground />

        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
          <Link href="/" className="mb-8 animate-fade-in">
            <Image src="/logo.png" alt="LaunchPAID Logo" width={180} height={40} className="h-10 w-auto" />
          </Link>

          <div className="w-full max-w-md bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl rounded-xl p-8 text-center shadow-2xl shadow-purple-500/10 animate-fade-in-up">
            <div className="flex justify-center mb-6">
              <div className="h-20 w-20 bg-red-600/20 rounded-full flex items-center justify-center animate-scale-in">
                <AlertCircle className="h-10 w-10 text-red-500 animate-bounce-in" />
              </div>
            </div>
            <h1 className="text-3xl font-bold mb-4 text-red-400">Verification Failed</h1>
            <p className="text-gray-300 mb-6">
              {errorMessage || "Failed to verify your email. The link may be expired or invalid."}
            </p>
            <div className="space-y-3">
              <Button
                onClick={handleResendEmail}
                disabled={resending}
                className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-medium"
              >
                {resending ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Sending...
                  </div>
                ) : (
                  "Resend Verification Email"
                )}
              </Button>
              <Link href="/auth/signup">
                <Button variant="outline" className="w-full h-12 border-purple-500 text-white hover:bg-purple-500/10">
                  Sign Up Again
                </Button>
              </Link>
            </div>
          </div>
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
          <Image src="/logo.png" alt="LaunchPAID Logo" width={180} height={40} className="h-10 w-auto" />
        </Link>

        {/* Verification Card */}
        <div
          className="w-full max-w-md bg-gray-900/80 border border-gray-700/50 backdrop-blur-xl rounded-xl p-8 text-center shadow-2xl shadow-purple-500/10 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          <div className="flex justify-center mb-6">
            <div className="h-20 w-20 bg-purple-600/20 rounded-full flex items-center justify-center animate-scale-in">
              {verifying ? (
                <Loader2 className="h-10 w-10 text-purple-500 animate-spin" />
              ) : (
              <MailCheck className="h-10 w-10 text-purple-500 animate-bounce-in" />
              )}
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-4 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
            {verifying ? "Verifying..." : "Verify Your Email"}
          </h1>
          <p className="text-gray-300 mb-6 animate-fade-in-up" style={{ animationDelay: "0.6s" }}>
            {verifying 
              ? "Please wait while we verify your email address..."
              : "We've sent a verification link to your email address. Please check your inbox (and spam folder!) to activate your account."
            }
          </p>

          {!verifying && (
          <div className="flex flex-col gap-0 animate-fade-in-up" style={{ animationDelay: "0.8s" }}>
            <Button
              onClick={handleResendEmail}
              disabled={resending}
              className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-medium transition-all duration-200 hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/25 rounded-xl"
            >
              {resending ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Resending...
                </div>
              ) : resendSuccess ? (
                <div className="flex items-center gap-2">
                  <MailCheck className="h-4 w-4" />
                  Link Sent!
                </div>
              ) : (
                "Resend Verification Email"
              )}
            </Button>
            <Link href="/auth/login" className="w-full mt-4">
              <Button
                variant="outline"
                className="w-full h-12 border-purple-500 text-white hover:bg-purple-500/10 bg-transparent transition-all duration-200 hover:scale-[1.02] rounded-xl"
              >
                Go to Login <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
          )}

          <p className="text-xs text-gray-500 mt-8 animate-fade-in" style={{ animationDelay: "1s" }}>
            Having trouble? Contact support.
          </p>
        </div>

        {/* Footer */}
        <p className="text-xs text-gray-600 mt-8 text-center animate-fade-in" style={{ animationDelay: "1.2s" }}>
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

    @keyframes scale-in {
      from {
        opacity: 0;
        transform: scale(0.8);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    @keyframes bounce-in {
      0% { transform: scale(0.1); opacity: 0; }
      60% { transform: scale(1.2); opacity: 1; }
      100% { transform: scale(1); }
    }

    .animate-fade-in {
      animation: fade-in 0.6s ease-out forwards;
    }

    .animate-fade-in-up {
      animation: fade-in-up 0.6s ease-out forwards;
    }

    .animate-scale-in {
      animation: scale-in 0.5s ease-out forwards;
    }

    .animate-bounce-in {
      animation: bounce-in 0.7s ease-out forwards;
    }
  `}</style>
    </div>
  )
}

export default function VerificationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <VerificationContent />
    </Suspense>
  )
}
