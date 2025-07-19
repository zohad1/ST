interface EmailLayoutProps {
  title: string
  previewText?: string
  content: string
}

export function renderEmailLayout({ title, previewText, content }: EmailLayoutProps): string {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>${title}</title>
        ${previewText ? `<meta name="description" content="${previewText}" />` : ''}
        <style>
          body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #000000;
            color: #ffffff;
          }
          .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #000000;
          }
          .header {
            padding: 32px 24px;
            text-align: center;
            border-bottom: 1px solid #1f2937;
          }
          .logo {
            height: 40px;
            width: auto;
          }
          .content {
            padding: 32px 24px;
            background-color: #000000;
          }
          .footer {
            padding: 24px;
            text-align: center;
            background-color: #111827;
            border-top: 1px solid #1f2937;
          }
          .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #9333ea;
            color: #ffffff;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            margin: 16px 0;
          }
          .button:hover {
            background-color: #7c3aed;
          }
          .fallback-link {
            color: #9333ea;
            text-decoration: underline;
            font-size: 14px;
          }
          .text-muted {
            color: #9ca3af;
            font-size: 14px;
          }
          .text-center {
            text-align: center;
          }
          .mb-4 {
            margin-bottom: 16px;
          }
          .mb-6 {
            margin-bottom: 24px;
          }
          .mt-4 {
            margin-top: 16px;
          }
          .mt-6 {
            margin-top: 24px;
          }
          .p-6 {
            padding: 24px;
          }
          .rounded-lg {
            border-radius: 8px;
          }
          .border {
            border: 1px solid #1f2937;
          }
          .bg-gray-900 {
            background-color: #111827;
          }
          @media only screen and (max-width: 600px) {
            .email-container {
              width: 100% !important;
            }
            .content {
              padding: 24px 16px !important;
            }
            .header {
              padding: 24px 16px !important;
            }
          }
        </style>
      </head>
      <body>
        <div class="email-container">
          <!-- Header -->
          <div class="header">
            <img 
              src="https://launchpaid.ai/logo.png" 
              alt="LaunchPAID" 
              class="logo"
            />
          </div>

          <!-- Content -->
          <div class="content">
            ${content}
          </div>

          <!-- Footer -->
          <div class="footer">
            <div class="text-muted mb-4">
              <p>© 2024 LaunchPAID. All rights reserved.</p>
              <p>If you have any questions, contact us at support@launchpaid.ai</p>
            </div>
            <div class="text-muted">
              <p>This email was sent to you because you have an account with LaunchPAID.</p>
              <p>If you didn't request this email, you can safely ignore it.</p>
            </div>
          </div>
        </div>
      </body>
    </html>
  `
} 