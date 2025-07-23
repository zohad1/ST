"use client"

import { useState } from "react"
import { Bell, Search, ChevronDown } from "lucide-react"
import { useAuth } from "@/context/authContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAgencyBrands } from "@/hooks/useAgencyBrands"

interface AgencyHeaderProps {
  selectedBrand?: string
  onBrandChange?: (brandId: string) => void
}

export function AgencyHeader({ selectedBrand = "all", onBrandChange }: AgencyHeaderProps) {
  const [currentBrand, setCurrentBrand] = useState(selectedBrand)
  const { brands, loading, error } = useAgencyBrands()
  const { user, logout } = useAuth()

  const handleBrandChange = (brandId: string) => {
    setCurrentBrand(brandId)
    onBrandChange?.(brandId)
  }

  // Add "All Brands" option to the brands list
  const allBrands = [
    { id: "all", name: "All Brands", logo: "/placeholder.svg?height=24&width=24" },
    ...brands
  ]

  const selectedBrandData = allBrands.find((brand) => brand.id === currentBrand) || allBrands[0]

  return (
    <header className="h-16 border-b border-gray-800 bg-black flex items-center justify-between px-6">
      {/* Brand Selector */}
      <div className="flex items-center gap-4">
        <Select value={currentBrand} onValueChange={handleBrandChange}>
          <SelectTrigger className="w-[200px] bg-gray-900 border-gray-800 focus:border-purple-500">
            <div className="flex items-center gap-2">
              <img
                src={selectedBrandData.logo || "/placeholder.svg"}
                alt={selectedBrandData.name}
                className="h-5 w-5 rounded"
              />
              <SelectValue placeholder="Select Brand" />
            </div>
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-gray-800">
            {loading ? (
              <div className="px-2 py-1.5 text-sm text-gray-400">Loading brands...</div>
            ) : error ? (
              <div className="px-2 py-1.5 text-sm text-red-400">Failed to load brands</div>
            ) : allBrands.length === 0 ? (
              <div className="px-2 py-1.5 text-sm text-gray-400">No brands available</div>
            ) : (
              allBrands.map((brand) => (
                <SelectItem key={brand.id} value={brand.id} className="focus:bg-gray-800">
                  <div className="flex items-center gap-2">
                    <img src={brand.logo || "/placeholder.svg"} alt={brand.name} className="h-4 w-4 rounded" />
                    <span>{brand.name}</span>
                  </div>
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>

        {currentBrand !== "all" && (
          <div className="text-sm text-gray-400">
            Showing data for <span className="text-purple-400 font-medium">{selectedBrandData.name}</span>
          </div>
        )}
      </div>

      {/* Search Bar */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search campaigns, creators, or content..."
            className="pl-10 bg-gray-900 border-gray-800 focus:border-purple-500 focus:ring-purple-500"
          />
        </div>
      </div>

      {/* User Actions */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="h-5 w-5" />
          {/* TODO: Add real notification count when API is available */}
          {/* <span className="absolute -top-1 -right-1 h-3 w-3 bg-purple-600 rounded-full"></span> */}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-purple-600/20 flex items-center justify-center">
                <span className="font-bold text-sm">
                  {user?.first_name?.charAt(0) || (user as any)?.firstName?.charAt(0) || user?.username?.charAt(0) || "A"}
                </span>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium">
                  {user?.display_name || user?.first_name || user?.username || "Agency"}
                </p>
                <p className="text-xs text-purple-400">Agency</p>
              </div>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Agency Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile Settings</DropdownMenuItem>
            <DropdownMenuItem>Team Management</DropdownMenuItem>
            <DropdownMenuItem>Billing</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>Sign Out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
