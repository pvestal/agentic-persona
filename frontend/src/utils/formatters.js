import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Date formatting
export function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

export function formatRelativeTime(date) {
  if (!date) return '-'
  return dayjs(date).fromNow()
}

// Status formatting
export function getStatusType(status) {
  const statusMap = {
    'pending': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

export function getStatusLabel(status) {
  const labelMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'failed': 'Failed',
    'cancelled': 'Cancelled'
  }
  return labelMap[status] || status
}

// Priority formatting
export function getPriorityType(priority) {
  const priorityMap = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return priorityMap[priority] || 'info'
}

export function getPriorityLabel(priority) {
  const labelMap = {
    'low': 'Low',
    'medium': 'Medium',
    'high': 'High',
    'critical': 'Critical'
  }
  return labelMap[priority] || priority
}

// Number formatting
export function formatNumber(num, decimals = 0) {
  if (num === null || num === undefined) return '-'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num)
}

export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '-'
  return `${(value * 100).toFixed(decimals)}%`
}

export function formatDuration(seconds) {
  if (!seconds) return '-'
  
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}m ${secs.toFixed(0)}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

// File size formatting
export function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`
}

// Truncate text
export function truncateText(text, length = 100) {
  if (!text || text.length <= length) return text
  return `${text.substring(0, length)}...`
}

// Format JSON for display
export function formatJSON(obj, indent = 2) {
  try {
    return JSON.stringify(obj, null, indent)
  } catch (e) {
    return String(obj)
  }
}