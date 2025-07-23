"use client"

import React from "react"
import { Button } from "@/components/ui/button"

interface UserTypeToggleProps {
  value: string
  onChange: (value: string) => void
}

export function UserTypeToggle({ value, onChange }: UserTypeToggleProps) {
  return (
    <div className="flex space-x-2">
      <Button
        type="button"
        variant={value === "creator" ? "default" : "outline"}
        onClick={() => onChange("creator")}
        className="flex-1"
      >
        Creator
      </Button>
      <Button
        type="button"
        variant={value === "brand" ? "default" : "outline"}
        onClick={() => onChange("brand")}
        className="flex-1"
      >
        Brand
      </Button>
    </div>
  )
}
