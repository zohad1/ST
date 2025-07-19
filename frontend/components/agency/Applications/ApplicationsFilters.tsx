import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Search, Calendar, SlidersHorizontal } from "lucide-react"

interface ApplicationsFiltersProps {
  searchQuery: string
  onSearchChange: (value: string) => void
  statusFilter: string
  onStatusChange: (value: string) => void
  selectedCampaignId: string
  onCampaignChange: (value: string) => void
  campaigns: Array<{ id: string; name: string }>
  dateRange: { from?: Date; to?: Date } | undefined
  onDateRangeChange: (range: { from?: Date; to?: Date } | undefined) => void
  showFilters: boolean
  onShowFiltersChange: (show: boolean) => void
  statusOptions: string[]
}

export function ApplicationsFilters({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  selectedCampaignId,
  onCampaignChange,
  campaigns,
  dateRange,
  onDateRangeChange,
  showFilters,
  onShowFiltersChange,
  statusOptions
}: ApplicationsFiltersProps) {
  return (
    <div className="flex items-center gap-4 mb-4">
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search by name or email..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10 bg-gray-800 border-gray-700 text-white placeholder:text-gray-400"
        />
      </div>

      <Select value={statusFilter} onValueChange={onStatusChange}>
        <SelectTrigger className="w-40 bg-gray-800 border-gray-700">
          <SelectValue />
        </SelectTrigger>
        <SelectContent className="bg-gray-800 border-gray-700">
          {statusOptions.map((status) => (
            <SelectItem key={status} value={status} className="text-gray-300 hover:text-white">
              {status === "All" ? "All Status" : status.charAt(0).toUpperCase() + status.slice(1)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={selectedCampaignId} onValueChange={onCampaignChange}>
        <SelectTrigger className="w-48 bg-gray-800 border-gray-700">
          <SelectValue placeholder="Select Campaign" />
        </SelectTrigger>
        <SelectContent className="bg-gray-800 border-gray-700">
          {campaigns.map((campaign) => (
            <SelectItem key={campaign.id} value={campaign.id} className="text-gray-300 hover:text-white">
              {campaign.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Sheet open={showFilters} onOpenChange={onShowFiltersChange}>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            className={`border-gray-700 ${showFilters ? "bg-purple-600/20 border-purple-500/30 text-purple-400" : "bg-gray-800 hover:bg-gray-700"}`}
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Advanced
          </Button>
        </SheetTrigger>
        <SheetContent side="right" className="w-96 bg-gray-900 border-gray-800">
          <SheetHeader>
            <SheetTitle className="text-white">Advanced Filters</SheetTitle>
            <SheetDescription className="text-gray-400">
              Filter applications by detailed criteria
            </SheetDescription>
          </SheetHeader>
          
          <div className="space-y-6 mt-6">
            <div>
              <Label className="text-white font-medium">Date Range</Label>
              <div className="mt-2 space-y-2">
                <Button variant="outline" className="w-full justify-start border-gray-700 bg-gray-800 hover:bg-gray-700">
                  <Calendar className="h-4 w-4 mr-2" />
                  Select date range
                </Button>
              </div>
            </div>

            <div>
              <Label className="text-white font-medium">Creator Metrics</Label>
              <div className="mt-2 space-y-3">
                <div>
                  <Label className="text-sm text-gray-400">Minimum Followers</Label>
                  <Input 
                    type="number" 
                    placeholder="e.g., 10000" 
                    className="mt-1 bg-gray-800 border-gray-700 text-white"
                  />
                </div>
                <div>
                  <Label className="text-sm text-gray-400">Engagement Rate (%)</Label>
                  <Input 
                    type="number" 
                    placeholder="e.g., 3.5" 
                    className="mt-1 bg-gray-800 border-gray-700 text-white"
                  />
                </div>
              </div>
            </div>

            <div>
              <Label className="text-white font-medium">Profile Completion</Label>
              <div className="mt-2 space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox id="complete" className="border-gray-600" />
                  <Label htmlFor="complete" className="text-sm text-gray-300">Complete profiles only</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="incomplete" className="border-gray-600" />
                  <Label htmlFor="incomplete" className="text-sm text-gray-300">Include incomplete profiles</Label>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-800">
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1 border-gray-700 bg-gray-800 hover:bg-gray-700"
                  onClick={() => {
                    // Reset filters
                    onSearchChange("")
                    onStatusChange("All")
                    onDateRangeChange(undefined)
                  }}
                >
                  Clear Filters
                </Button>
                <Button 
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                  onClick={() => onShowFiltersChange(false)}
                >
                  Apply Filters
                </Button>
              </div>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
} 