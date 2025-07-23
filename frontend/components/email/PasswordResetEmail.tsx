interface PasswordResetEmailProps {
  userName: string
  resetUrl: string
  fallbackUrl?: string
  expiresIn?: string
}

export function renderPasswordResetEmail({ 
  userName, 
  resetUrl, 
  fallbackUrl,
  expiresIn = "1 hour"
}: PasswordResetEmailProps): string {
  const content = `
    <div class="text-center mb-6">
      <h1 style="font-size: 28px; font-weight: bold; margin-bottom: 16px; color: #ffffff;">
        Reset Your Password 🔐
      </h1>
      <p style="font-size: 16px; color: #9ca3af; margin-bottom: 24px;">
        Hi ${userName}, we received a request to reset your password.
      </p>
    </div>

    <div class="bg-gray-900 border rounded-lg p-6 mb-6">
      <div class="text-center mb-6">
        <div style="width: 64px; height: 64px; background-color: #dc2626; border-radius: 50%; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center;">
          <span style="font-size: 24px; color: #ffffff;">🔒</span>
        </div>
        <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #ffffff;">
          Secure Password Reset
        </h2>
        <p style="font-size: 14px; color: #9ca3af;">
          Click the button below to create a new password for your LaunchPAID account.
        </p>
      </div>

      <div class="text-center">
        <a 
          href="${resetUrl}"
          class="button"
          style="display: inline-block; padding: 12px 32px; background-color: #dc2626; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 16px; margin: 16px 0;">
          Reset Password
        </a>
        
        ${fallbackUrl ? `
          <div class="mt-4">
            <p style="font-size: 14px; color: #9ca3af; margin-bottom: 8px;">
              If the button above doesn't work, click the link below:
            </p>
            <a 
              href="${fallbackUrl}"
              class="fallback-link"
              style="color: #dc2626; text-decoration: underline; font-size: 14px;">
              ${fallbackUrl}
            </a>
          </div>
        ` : ''}
      </div>
    </div>

    <div class="bg-gray-900 border rounded-lg p-6 mb-6">
      <h3 style="font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #ffffff;">
        ⚠️ Security Notice
      </h3>
      <ul style="font-size: 14px; color: #9ca3af; padding-left: 20px;">
        <li style="margin-bottom: 8px;">
          This link will expire in ${expiresIn}
        </li>
        <li style="margin-bottom: 8px;">
          If you didn't request this password reset, please ignore this email
        </li>
        <li style="margin-bottom: 8px;">
          Your current password will remain unchanged until you complete the reset
        </li>
        <li>
          For security, this link can only be used once
        </li>
      </ul>
    </div>

    <div class="text-muted text-center">
      <p style="font-size: 14px; margin-bottom: 8px;">
        Need help? Contact our support team at support@launchpaid.ai
      </p>
      <p style="font-size: 14px;">
        This is an automated message from LaunchPAID. Please do not reply to this email.
      </p>
    </div>
  `

  return content
} 