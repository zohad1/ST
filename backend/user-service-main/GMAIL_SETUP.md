# Gmail Setup for LaunchPaid Email System

## 🚀 Quick Setup for Gmail

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to "Security"
3. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to your Google Account settings
2. Navigate to "Security" → "2-Step Verification"
3. Scroll down to "App passwords"
4. Click "Generate new app password"
5. Select "Mail" and "Other (Custom name)"
6. Name it "LaunchPaid" and click "Generate"
7. **Copy the 16-character password** (this is your `SMTP_PASSWORD`)

### Step 3: Configure Environment Variables
Create a `.env` file in `backend/user-service-main/` with:

```env
# Email Configuration
MAIL_ENABLED=true
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=LaunchPAID

# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_TLS=true

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Step 4: Test the Setup
1. Start your backend server
2. Try signing up a new user
3. Check if verification email is sent
4. Check your Gmail logs for any errors

## 🔧 Troubleshooting

### Common Issues:

**1. "Authentication failed" error:**
- Make sure you're using the **App Password**, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled
- Double-check the 16-character app password

**2. "Connection failed" error:**
- Verify `SMTP_HOST=smtp.gmail.com`
- Verify `SMTP_PORT=587`
- Verify `SMTP_TLS=true`

**3. Emails not sending:**
- Check if `MAIL_ENABLED=true`
- Verify all environment variables are set
- Check backend logs for detailed error messages

**4. Emails going to spam:**
- This is normal for new email addresses
- Users should check their spam folder
- Consider using Mailgun for production

## 📧 Email Types Supported

1. **Verification Email** - Sent when user signs up
2. **Password Reset Email** - Sent when user requests password reset
3. **Welcome Email** - Sent after successful email verification

## 🎨 Email Templates

All emails include:
- LaunchPaid branding and colors
- Professional HTML layout
- Plain text fallback
- Responsive design
- Clear call-to-action buttons

## 🔒 Security Notes

- App passwords are more secure than regular passwords
- Each app password is unique and can be revoked
- Never commit your `.env` file to version control
- Use different app passwords for development and production

## 🚀 Production Considerations

For production, consider:
1. **Mailgun** - Better deliverability and analytics
2. **Domain verification** - Professional email addresses
3. **SPF/DKIM records** - Improve email deliverability
4. **Email templates** - More sophisticated designs

## 📝 Example .env File

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/launchpaid_users

# Security Keys
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Email Configuration
MAIL_ENABLED=true
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=LaunchPAID

# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_TLS=true

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

## ✅ Testing Checklist

- [ ] 2-Factor Authentication enabled
- [ ] App password generated
- [ ] Environment variables configured
- [ ] Backend server started
- [ ] Signup flow tested
- [ ] Verification email received
- [ ] Password reset flow tested
- [ ] Welcome email received

## 🆘 Need Help?

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Verify all environment variables are correct
3. Test with a different Gmail account
4. Consider using Mailgun for better reliability 