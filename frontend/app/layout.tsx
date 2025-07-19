import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { QueryProvider } from "@/providers/QueryProvider"
import { AuthProvider } from "@/context/authContext"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "LaunchPAID - Creator CRM & Campaign Management",
  description:
    "The ultimate CRM platform for TikTok creators and brands to manage campaigns, track performance, and maximize revenue.",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryProvider>
          <AuthProvider>
            <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
              {children}
            </ThemeProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
}
