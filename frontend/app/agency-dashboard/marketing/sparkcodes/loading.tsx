import { AgencyHeader } from "@/components/agency/navigation/agency-header"
import { AgencySidebar } from "@/components/agency/navigation/agency-sidebar"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export default function SparkCodesLoading() {
  return (
    <div className="min-h-screen bg-black">
      <AgencySidebar />

      <div className="lg:pl-60">
        <AgencyHeader />

        <main className="p-6">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
              <span>Marketing</span>
              <span>/</span>
              <span className="text-purple-400">Spark Codes</span>
            </div>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <Skeleton className="h-8 w-80 mb-2 bg-gray-800" />
                <Skeleton className="h-4 w-96 bg-gray-800" />
              </div>
              <div className="flex gap-3">
                <Skeleton className="h-10 w-32 bg-gray-800" />
                <Skeleton className="h-10 w-32 bg-gray-800" />
                <Skeleton className="h-10 w-40 bg-gray-800" />
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <Card key={i} className="bg-gray-900 border-gray-800">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-24 bg-gray-800" />
                  <Skeleton className="h-4 w-4 bg-gray-800" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-20 mb-2 bg-gray-800" />
                  <Skeleton className="h-4 w-16 bg-gray-800" />
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Main Content */}
          <div className="space-y-6">
            <Skeleton className="h-12 w-full bg-gray-800" />
            <Card className="bg-gray-900 border-gray-800">
              <CardContent className="p-6">
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex items-center gap-4">
                      <Skeleton className="h-4 w-4 bg-gray-800" />
                      <Skeleton className="h-10 w-10 rounded-full bg-gray-800" />
                      <Skeleton className="h-4 w-32 bg-gray-800" />
                      <Skeleton className="h-4 w-24 bg-gray-800" />
                      <Skeleton className="h-4 w-20 bg-gray-800" />
                      <Skeleton className="h-4 w-16 bg-gray-800" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
