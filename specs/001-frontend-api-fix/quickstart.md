# Quickstart Guide: Frontend API Client Fixes

## Overview
This guide provides instructions for setting up and running the frontend application with proper API client configuration and Tailwind CSS styling.

## Prerequisites
- Node.js 18+ and npm/yarn/pnpm
- Access to the backend API server
- Properly configured environment variables

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd todo-phase-II
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
# or
pnpm install
```

### 3. Configure Environment Variables
Create a `.env.local` file in the frontend directory and add the required variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
NEXT_PUBLIC_API_BASE_PATH="/api/v1"

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000"
NEXT_PUBLIC_BETTER_AUTH_BASE_PATH="/api/auth"
```

### 4. Set Up Tailwind CSS
Install Tailwind CSS and its dependencies:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Configure `tailwind.config.js`:
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

Create `src/app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 5. Run the Application
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

## Verification Steps

### 1. Check Environment Variables
After starting the application, verify that the API URL is properly configured:
- Open browser developer tools
- Check the Network tab for API requests
- Verify URLs start with the configured NEXT_PUBLIC_API_URL

### 2. Test Registration Flow
Navigate to `/auth/sign-up` and verify:
- Page renders with proper Tailwind CSS styling
- Form fields have appropriate styling
- Submit button is styled correctly
- Error messages display with proper styling

### 3. Check API Communication
- Submit registration form with valid data
- Verify API request goes to the correct URL (not containing "undefined")
- Check for successful response handling
- Ensure no JSON parse errors occur

### 4. Verify Styling
- All UI elements should have proper Tailwind CSS classes applied
- Layout should be responsive and visually appealing
- Forms should have proper spacing and styling
- Error messages should be visually distinct

## Troubleshooting

### Environment Variable Issues
If you see "undefined" in API URLs:
1. Verify `.env.local` file exists with `NEXT_PUBLIC_API_URL` variable
2. Check that the variable name starts with `NEXT_PUBLIC_` prefix
3. Restart the development server after making changes to environment files

### Tailwind CSS Not Working
If styling is not applied:
1. Verify `tailwind.config.js` is properly configured
2. Check that `globals.css` imports Tailwind directives
3. Ensure CSS file is imported in the root layout
4. Restart the development server after configuration changes

### JSON Parse Errors
If authentication pages show JSON parse errors:
1. Verify backend API is running and accessible
2. Check CORS configuration on the backend
3. Ensure API responses are in correct JSON format
4. Verify network requests are reaching the correct endpoints

## Expected Outcomes
After applying the fixes:
- API calls use correct base URLs without "undefined" in endpoints (100% of requests)
- Tailwind CSS styling is properly applied to all UI components (100% of components)
- No JSON parse errors occur during authentication flows
- Registration flow completes successfully without errors (100% of attempts)
- UI renders with professional styling meeting design standards
- Users can complete the full registration process from browser in under 2 minutes