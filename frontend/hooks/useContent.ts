// hooks/useContent.ts
import { useState, useEffect } from 'react'
import { campaignServiceClient, sharedServiceClient } from '@/lib/api/client'
import type { ApiResponse } from '@/lib/api/client'

// Types for content items
export interface ContentItem {
  id: string
  name: string
  type: "video" | "image" | "document" | "other"
  url: string
  thumbnail?: string
  size: string
  uploadDate: string
  campaign?: string
  tags: string[]
  status: "pending" | "approved" | "rejected" | "draft"
  views?: number
  source: 'deliverable' | 'upload' // Track where the content came from
}

// Backend deliverable type
interface Deliverable {
  id: string
  campaign_id: string
  creator_id: string
  application_id: string
  deliverable_number: number
  title?: string
  description?: string
  tiktok_post_url?: string
  post_caption?: string
  content_url?: string
  content_type?: string
  hashtags_used?: string[]
  status: 'pending' | 'submitted' | 'approved' | 'rejected' | 'revision_requested'
  views?: number
  likes?: number
  comments?: number
  shares?: number
  gmv_generated?: number
  due_date?: string
  submitted_at?: string
  reviewed_at?: string
  created_at: string
  updated_at: string
  campaign?: {
    id: string
    name: string
    description?: string
  }
}

// Backend file upload type
interface UploadedFile {
  id: string
  filename: string
  original_name: string
  file_type: string
  file_size: number
  file_url: string
  folder?: string
  uploaded_at: string
  created_by: string
}

interface DeliverablesResponse {
  deliverables?: Deliverable[]
  data?: Deliverable[]
  [key: string]: any
}

interface FilesResponse {
  files?: UploadedFile[]
  data?: UploadedFile[]
  [key: string]: any
}

export function useContent() {
  const [content, setContent] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Helper function to determine content type from URL or file type
  const getContentType = (url: string, fileType?: string): "video" | "image" | "document" | "other" => {
    const extension = url.split('.').pop()?.toLowerCase() || ''
    const mimeType = fileType?.toLowerCase() || ''
    
    // Video types
    if (mimeType.includes('video') || ['mp4', 'mov', 'avi', 'webm', 'mkv'].includes(extension)) {
      return 'video'
    }
    
    // Image types
    if (mimeType.includes('image') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension)) {
      return 'image'
    }
    
    // Document types
    if (mimeType.includes('document') || mimeType.includes('pdf') || 
        ['pdf', 'doc', 'docx', 'txt', 'rtf'].includes(extension)) {
      return 'document'
    }
    
    return 'other'
  }

  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Transform deliverable to content item
  const transformDeliverable = (deliverable: Deliverable): ContentItem => {
    const contentUrl = deliverable.tiktok_post_url || deliverable.content_url || ''
    const contentType = getContentType(contentUrl, deliverable.content_type)
    
    return {
      id: deliverable.id,
      name: deliverable.title || `Deliverable #${deliverable.deliverable_number}`,
      type: contentType,
      url: contentUrl,
      thumbnail: contentType === 'image' ? contentUrl : undefined,
      size: 'Unknown', // Deliverables don't typically have file size info
      uploadDate: deliverable.submitted_at || deliverable.created_at,
      campaign: deliverable.campaign?.name,
      tags: deliverable.hashtags_used || [],
      status: deliverable.status === 'submitted' ? 'pending' : 
              deliverable.status === 'approved' ? 'approved' : 
              deliverable.status === 'rejected' ? 'rejected' : 'draft',
      views: deliverable.views,
      source: 'deliverable'
    }
  }

  // Transform uploaded file to content item
  const transformUploadedFile = (file: UploadedFile): ContentItem => {
    const contentType = getContentType(file.file_url, file.file_type)
    
    return {
      id: file.id,
      name: file.original_name,
      type: contentType,
      url: file.file_url,
      thumbnail: contentType === 'image' ? file.file_url : undefined,
      size: formatFileSize(file.file_size),
      uploadDate: file.uploaded_at,
      campaign: file.folder, // Use folder as campaign indicator
      tags: [], // Uploaded files don't have tags by default
      status: 'approved', // Uploaded files are considered approved
      source: 'upload'
    }
  }

  const fetchContent = async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('🚀 Fetching content from backend...')

      // Fetch deliverables and uploaded files in parallel
      const [deliverablesResponse, filesResponse] = await Promise.allSettled([
        campaignServiceClient.get<DeliverablesResponse>('/api/v1/deliverables/my-deliverables'),
        sharedServiceClient.get<FilesResponse>('/api/v1/shared/files') // This might need to be adjusted based on actual endpoint
      ])

      let allContent: ContentItem[] = []

      // Process deliverables
      if (deliverablesResponse.status === 'fulfilled' && deliverablesResponse.value.success) {
        const response = deliverablesResponse.value
        let deliverableData: Deliverable[] = []
        
        if (Array.isArray(response.data)) {
          deliverableData = response.data
        } else if (response.data?.deliverables && Array.isArray(response.data.deliverables)) {
          deliverableData = response.data.deliverables
        } else if (response.data?.data && Array.isArray(response.data.data)) {
          deliverableData = response.data.data
        }

        const deliverableContent = deliverableData.map(transformDeliverable)
        allContent.push(...deliverableContent)
        console.log('✅ Successfully fetched deliverables:', deliverableContent.length)
      } else {
        console.warn('⚠️ Failed to fetch deliverables:', 
          deliverablesResponse.status === 'fulfilled' ? deliverablesResponse.value.error : 'Request failed')
      }

      // Process uploaded files (optional - might not be available)
      if (filesResponse.status === 'fulfilled' && filesResponse.value.success) {
        const response = filesResponse.value
        let fileData: UploadedFile[] = []
        
        if (Array.isArray(response.data)) {
          fileData = response.data
        } else if (response.data?.files && Array.isArray(response.data.files)) {
          fileData = response.data.files
        } else if (response.data?.data && Array.isArray(response.data.data)) {
          fileData = response.data.data
        }

        const uploadedContent = fileData.map(transformUploadedFile)
        allContent.push(...uploadedContent)
        console.log('✅ Successfully fetched uploaded files:', uploadedContent.length)
      } else {
        console.warn('⚠️ Failed to fetch uploaded files (this might be expected if endpoint doesn\'t exist):', 
          filesResponse.status === 'fulfilled' ? filesResponse.value.error : 'Request failed')
      }

      // Sort content by upload date (newest first)
      allContent.sort((a, b) => new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime())

      setContent(allContent)
      console.log('✅ Successfully loaded all content:', allContent.length, 'items')

    } catch (err: any) {
      console.error('❌ Content fetch error:', err)
      setError(err.message || 'Failed to load content')
      setContent([])
    } finally {
      setLoading(false)
    }
  }

  // Upload new content
  const uploadFile = async (file: File, options?: { folder?: string }) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (options?.folder) {
        formData.append('folder', options.folder)
      }

      const response = await sharedServiceClient.upload<UploadedFile>('/api/v1/shared/upload', formData)

      if (response.success && response.data) {
        // Add the new file to the content list
        const newContent = transformUploadedFile(response.data)
        setContent(prev => [newContent, ...prev])
        return { success: true, data: response.data }
      } else {
        throw new Error(response.error || 'Upload failed')
      }
    } catch (err: any) {
      console.error('❌ Upload error:', err)
      return { success: false, error: err.message || 'Upload failed' }
    }
  }

  // Delete content
  const deleteContent = async (contentId: string, source: 'deliverable' | 'upload') => {
    try {
      let response: ApiResponse<any>

      if (source === 'upload') {
        response = await sharedServiceClient.delete(`/api/v1/shared/files/${contentId}`)
      } else {
        response = await campaignServiceClient.delete(`/api/v1/deliverables/${contentId}`)
      }

      if (response.success) {
        // Remove the content from the list
        setContent(prev => prev.filter(item => item.id !== contentId))
        return { success: true }
      } else {
        throw new Error(response.error || 'Delete failed')
      }
    } catch (err: any) {
      console.error('❌ Delete error:', err)
      return { success: false, error: err.message || 'Delete failed' }
    }
  }

  useEffect(() => {
    fetchContent()
  }, [])

  return {
    content,
    loading,
    error,
    refetch: fetchContent,
    uploadFile,
    deleteContent
  }
} 