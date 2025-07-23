interface VerificationEmailProps {
  userName: string
  verificationUrl: string
  fallbackUrl?: string
}

export function renderVerificationEmail({ 
  userName, 
  verificationUrl, 
  fallbackUrl 
}: VerificationEmailProps): string {
  const content = `
    <div class="text-center mb-6">
      <h1 style="font-size: 28px; font-weight: bold; margin-bottom: 16px; color: #ffffff;">
        Welcome to LaunchPAID! 🚀
      </h1>
      <p style="font-size: 16px; color: #9ca3af; margin-bottom: 24px;">
        Hi ${userName}, we're excited to have you on board!
      </p>
    </div>

    <div class="bg-gray-900 border rounded-lg p-6 mb-6">
      <div class="text-center mb-6">
        <div style="width: 64px; height: 64px; background-color: #9333ea; border-radius: 50%; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center;">
          <span style="font-size: 24px;">✓</span>
        </div>
        <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #ffffff;">
          Verify Your Email Address
        </h2>
        <p style="font-size: 14px; color: #9ca3af;">
          To complete your account setup and start using LaunchPAID, please verify your email address.
        </p>
      </div>

      <div class="text-center">
        <a 
          href="${verificationUrl}"
          class="button"
          style="display: inline-block; padding: 12px 32px; background-color: #9333ea; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 16px; margin: 16px 0;">
          Verify Email Address
        </a>
        
        ${fallbackUrl ? `
          <div class="mt-4">
            <p style="font-size: 14px; color: #9ca3af; margin-bottom: 8px;">
              If the button above doesn't work, click the link below:
            </p>
            <a 
              href="${fallbackUrl}"
              class="fallback-link"
              style="color: #9333ea; text-decoration: underline; font-size: 14px;">
              ${fallbackUrl}
            </a>
          </div>
        ` : ''}
      </div>
    </div>

    <div class="text-muted text-center">
      <p style="font-size: 14px; margin-bottom: 8px;">
        This verification link will expire in 24 hours.
      </p>
      <p style="font-size: 14px;">
        If you didn't create a LaunchPAID account, you can safely ignore this email.
      </p>
    </div>
  `

  return content
} 