interface WelcomeEmailProps {
  userName: string
  userRole: "creator" | "agency" | "brand"
  dashboardUrl: string
}

export function renderWelcomeEmail({ 
  userName, 
  userRole, 
  dashboardUrl 
}: WelcomeEmailProps): string {
  const getRoleContent = () => {
    switch (userRole) {
      case "creator":
        return {
          title: "Welcome to LaunchPAID, Creator! 🎬",
          subtitle: "Ready to maximize your TikTok earnings?",
          features: [
            "Track your GMV and earnings across all campaigns",
            "Unlock achievement badges and bonuses",
            "Manage your content and deliverables",
            "Connect with top brands and agencies"
          ],
          ctaText: "Access Your Creator Dashboard",
          nextSteps: [
            "Complete your profile and bio",
            "Connect your TikTok account",
            "Browse available campaigns",
            "Set up your payment preferences"
          ]
        }
      case "agency":
        return {
          title: "Welcome to LaunchPAID, Agency! 🏢",
          subtitle: "Ready to scale your creator campaigns?",
          features: [
            "Manage multiple clients and campaigns",
            "Track ROI and performance metrics",
            "Collaborate with your team members",
            "Access comprehensive analytics"
          ],
          ctaText: "Access Your Agency Dashboard",
          nextSteps: [
            "Set up your agency profile",
            "Invite team members",
            "Connect your client accounts",
            "Create your first campaign"
          ]
        }
      case "brand":
        return {
          title: "Welcome to LaunchPAID, Brand! 🏆",
          subtitle: "Ready to launch successful creator campaigns?",
          features: [
            "Find and collaborate with top creators",
            "Track campaign performance and ROI",
            "Manage campaign budgets and payouts",
            "Access detailed analytics and insights"
          ],
          ctaText: "Access Your Brand Dashboard",
          nextSteps: [
            "Complete your brand profile",
            "Set up your campaign budget",
            "Browse available creators",
            "Create your first campaign"
          ]
        }
      default:
        return {
          title: "Welcome to LaunchPAID! 🚀",
          subtitle: "Ready to get started?",
          features: [
            "Manage your campaigns and content",
            "Track performance and earnings",
            "Connect with creators and brands",
            "Access powerful analytics"
          ],
          ctaText: "Access Your Dashboard",
          nextSteps: [
            "Complete your profile",
            "Explore the platform",
            "Connect your accounts",
            "Start your first campaign"
          ]
        }
    }
  }

  const content = getRoleContent()

  const emailContent = `
    <div class="text-center mb-6">
      <h1 style="font-size: 28px; font-weight: bold; margin-bottom: 16px; color: #ffffff;">
        ${content.title}
      </h1>
      <p style="font-size: 16px; color: #9ca3af; margin-bottom: 24px;">
        Hi ${userName}, ${content.subtitle}
      </p>
    </div>

    <div class="bg-gray-900 border rounded-lg p-6 mb-6">
      <div class="text-center mb-6">
        <div style="width: 64px; height: 64px; background-color: #9333ea; border-radius: 50%; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center;">
          <span style="font-size: 24px;">🎉</span>
        </div>
        <h2 style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #ffffff;">
          Your LaunchPAID Journey Starts Now
        </h2>
        <p style="font-size: 14px; color: #9ca3af;">
          Here's what you can do with LaunchPAID:
        </p>
      </div>

      <div style="margin-bottom: 24px;">
        <ul style="font-size: 14px; color: #9ca3af; padding-left: 20px;">
          ${content.features.map(feature => `<li style="margin-bottom: 8px;">✓ ${feature}</li>`).join('')}
        </ul>
      </div>

      <div class="text-center">
        <a 
          href="${dashboardUrl}"
          class="button"
          style="display: inline-block; padding: 12px 32px; background-color: #9333ea; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 16px; margin: 16px 0;">
          ${content.ctaText}
        </a>
      </div>
    </div>

    <div class="bg-gray-900 border rounded-lg p-6 mb-6">
      <h3 style="font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #ffffff;">
        🚀 Next Steps to Get Started
      </h3>
      <ol style="font-size: 14px; color: #9ca3af; padding-left: 20px;">
        ${content.nextSteps.map(step => `<li style="margin-bottom: 8px;">${step}</li>`).join('')}
      </ol>
    </div>

    <div class="text-muted text-center">
      <p style="font-size: 14px; margin-bottom: 8px;">
        Need help getting started? Our support team is here to help!
      </p>
      <p style="font-size: 14px;">
        Contact us at support@launchpaid.ai or check out our documentation.
      </p>
    </div>
  `

  return emailContent
} 