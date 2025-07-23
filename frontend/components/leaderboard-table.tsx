import Image from "next/image"
import { Badge } from "@/components/ui/badge"
import { Trophy } from "lucide-react"
import { useLeaderboard } from "@/hooks/useLeaderboard"

export function LeaderboardTable() {
  const { leaderboardData, loading, error } = useLeaderboard()

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center gap-3 animate-pulse">
            <div className="h-8 w-8 rounded-full bg-gray-800"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-800 rounded w-3/4"></div>
              <div className="h-3 bg-gray-800 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-400 text-sm">Unable to load leaderboard</p>
        <p className="text-gray-500 text-xs mt-1">{error}</p>
      </div>
    )
  }

  // Show empty state
  if (!leaderboardData || leaderboardData.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-400 text-sm">No leaderboard data available</p>
        <p className="text-gray-500 text-xs mt-1">Check back later for updates</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left font-medium text-gray-400 py-3 px-4">Rank</th>
            <th className="text-left font-medium text-gray-400 py-3 px-4">Creator</th>
            <th className="text-left font-medium text-gray-400 py-3 px-4">Badge</th>
            <th className="text-right font-medium text-gray-400 py-3 px-4">GMV</th>
          </tr>
        </thead>
        <tbody>
          {leaderboardData.map((creator) => (
            <tr
              key={creator.rank}
              className={`border-b border-gray-800 ${creator.isCurrentUser ? "bg-purple-900/20" : ""}`}
            >
              <td className="py-3 px-4">
                {creator.rank === 1 && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-full bg-yellow-500/20">
                    <Trophy className="h-4 w-4 text-yellow-500" />
                  </div>
                )}
                {creator.rank === 2 && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-400/20">
                    <Trophy className="h-4 w-4 text-gray-400" />
                  </div>
                )}
                {creator.rank === 3 && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-full bg-amber-700/20">
                    <Trophy className="h-4 w-4 text-amber-700" />
                  </div>
                )}
                {creator.rank > 3 && (
                  <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-800">
                    <span className="text-sm font-medium">{creator.rank}</span>
                  </div>
                )}
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gray-800 overflow-hidden">
                    <Image
                      src={creator.avatar || "/placeholder.svg"}
                      alt={creator.name}
                      width={40}
                      height={40}
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <div>
                    <div className="font-medium">{creator.name}</div>
                    {creator.isCurrentUser && <div className="text-xs text-purple-400">You</div>}
                  </div>
                </div>
              </td>
              <td className="py-3 px-4">
                <Badge className="bg-purple-600/20 text-purple-400 hover:bg-purple-600/30">{creator.badge}</Badge>
              </td>
              <td className="py-3 px-4 text-right font-medium">${creator.gmv.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
