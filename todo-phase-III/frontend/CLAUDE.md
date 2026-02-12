# Frontend — TaskPulse AI

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript 5.3
- Tailwind CSS with PostCSS + Autoprefixer

## Project Structure

```
frontend/src/
  app/             # Next.js App Router pages and layouts
    auth/          # Sign-in and sign-up pages
  auth/            # Auth config (JWT token helpers)
  components/
    auth/          # Auth-related components
    chat/          # CUI (Chat) interface — ChatInterface.tsx
    tasks/         # GUI (Task board) — TaskBoard.tsx
    ui/            # Shared UI primitives (shadcn: Button, Input, Badge, ScrollArea)
  lib/             # API client (api-client.ts) and utils (cn helper)
  types/           # TypeScript type definitions
```

## Styling Rules

- Dark glassmorphism theme using OKLch color space
- Key utility classes: `glass-card`, `glass-card-elevated`, `glass-input`, `gradient-mesh`, `glow-primary`
- All custom theme tokens defined in `globals.css`
- Responsive: mobile-first with `sm:` and `lg:` breakpoints

## Auth Pattern

- JWT stored in browser `localStorage`
- `isAuthenticated()` guard in `auth/auth-config.ts` checks token existence and expiry
- `storeToken()` / `removeToken()` / `getToken()` helpers
- Unauthenticated users redirected to `/auth/sign-in`

## API Integration

- `lib/api-client.ts` exports `taskApi` and `authApi` clients
- `taskApi`: CRUD operations hitting `/api/v1/{user_id}/tasks/*`
- `authApi`: login, register, me, health hitting `/api/v1/auth/*`
- `getUserId()` extracts user ID from JWT payload
- All requests attach `Authorization: Bearer <token>` header

## Dual Interface

- **Tasks mode (GUI)**: Card-based task board with create/toggle/delete
- **Chat mode (CUI)**: Terminal-style command interface (`add`, `done`, `undo`, `delete`, `edit`, `list`)
- Mode toggle at top of dashboard page

## Code Standards

- `'use client'` directive on all interactive pages/components
- Prefer named exports for pages, default exports for components
- Use `cn()` utility from `lib/utils` for conditional class merging
