import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define protected routes and their required roles
const protectedRoutes = {
  '/agency-dashboard': ['agency'],
  '/client-dashboard': ['brand'],
  '/creator-dashboard': ['creator'],
}

// Define public routes that don't need authentication
const publicRoutes = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/verify-email',
  '/',
  '/unauthorized',
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if the route is public
  if (publicRoutes.includes(pathname)) {
    return NextResponse.next()
  }

  // Check if the route is protected
  const requiredRoles = protectedRoutes[pathname as keyof typeof protectedRoutes]
  
  if (requiredRoles) {
    // Get the token from cookies or headers
    const token = request.cookies.get('access_token')?.value || 
                  request.cookies.get('auth_token')?.value ||
                  request.headers.get('authorization')?.replace('Bearer ', '')

    if (!token) {
      // No token found, redirect to login
      const loginUrl = new URL('/auth/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Token exists, let the client-side auth handle role checking
    // The client-side auth will validate the token and check roles
    return NextResponse.next()
  }

  // For other routes, allow access
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
} 