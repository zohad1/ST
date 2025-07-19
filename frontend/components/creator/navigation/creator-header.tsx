// components/creator/navigation/creator-header.tsx
"use client"

import { Bell, Menu, Search, User } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Link from "next/link"

interface CreatorHeaderProps {
  onMobileMenuToggle: () => void
}

export function CreatorHeader({ onMobileMenuToggle }: CreatorHeaderProps) {
  const { user, logout } = useAuth()
  const avatarUrl = user?.profile_image_url || "/placeholder.svg?height=32&width=32"
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left side - Mobile menu button and search */}
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onMobileMenuToggle}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            <Menu className="h-6 w-6" />
          </Button>

          <div className="hidden sm:block">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search campaigns, content..."
                className="pl-10 w-64 bg-gray-800 border-gray-700 text-white placeholder-gray-400"
              />
            </div>
          </div>
        </div>

        {/* Right side - Notifications and user menu */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative text-gray-400 hover:text-white">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
              3
            </span>
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={avatarUrl} />
                  <AvatarFallback className="bg-purple-600 text-white">
                    {user?.first_name?.charAt(0) || (user as any)?.firstName?.charAt(0) || user?.username?.charAt(0) || "C"}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-gray-800 border-gray-700" align="end">
              <DropdownMenuLabel className="text-white">Creator Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem asChild className="text-gray-300 hover:text-white hover:bg-gray-700">
                <Link href="/creator-dashboard/profile" className="flex items-center w-full">
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="text-gray-300 hover:text-white hover:bg-gray-700">
                <Link href="/creator-dashboard/settings" className="flex items-center w-full">
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem
                onSelect={(e) => {
                  e.preventDefault()
                  logout()
                }}
                className="text-red-400 hover:text-red-300 hover:bg-gray-700 cursor-pointer"
              >
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
} 