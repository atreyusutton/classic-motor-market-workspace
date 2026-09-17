# Classic Motor Market — CLAUDE.md

Developer reference for Claude Code. This file is the single source of truth for working on this codebase. The root-level `stack.md`, `prompt.md`, `listing-flow.md`, `plan.md`, `database.md`, `vercel-deploy.md`, and `classic-motor-market/README.md` are superseded by this file and can be deleted.

## Team

| Person | Role |
|--------|------|
| Atreyu Sutton | CTO — platform, infrastructure, all code |
| Brian Hughes | Partnerships, marketing, community |
| Michael Burroughs | Partnerships, marketing, community |

---

## What This Is

Classic Motor Market (CMM) is a private, members-only classified marketplace for European classic and collector car enthusiasts. Think Bring a Trailer, but no auctions, European-focused, and explicitly designed to exclude tire-kickers via a membership paywall. The experience is old-school classifieds with modern privacy and security.

**Core principles:**
- Privacy first: seller emails never exposed, full VINs only for members
- Members get early access (10 minutes) to new listings before the public
- No auction mechanics — fixed-price listings only
- Membership is required to contact sellers or list vehicles

---

## Repository Layout

```
/                                    ← repo root
├── CLAUDE.md                        ← this file
├── stack.md                         ← SUPERSEDED — safe to delete
├── prompt.md                        ← SUPERSEDED — safe to delete
├── listing-flow.md                  ← SUPERSEDED — safe to delete
├── bulk-import-vehicles/            ← sample vehicle data (images + metadata) for seeding
│   ├── 1987-bmw-m3/
│   ├── 1971-alfa-romeo-gtv-2000/
│   ├── 1990-audi-coupe-quattro/
│   ├── 1973-volkswagen-1303/
│   ├── 1954-austin-healey-100-bn1/
│   ├── 1989-ferrari-328-gts/
│   ├── 1979-porsche-930-turbo/
│   ├── 1985-renault-r5-turbo-2/
│   └── 1994-land-rover-range-rover-county/
├── cmm-docs/
│   ├── designs/cmm-wireframes.pdf      ← UI wireframes reference
│   ├── fonts/                          ← font assets
│   ├── initial-prompt-docs.zip         ← archived original planning docs (stack, prompt, plan, db, etc.)
│   ├── legal/                          ← legal pages (website terms/privacy)
│   │   └── revisions/                  ← founders operating agreement drafts
│   │       ├── agreement-essentials.md ← what founders agreed to pre-lawyer
│   │       ├── operating-agreement.md  ← lawyer draft with ****EDIT**** annotations
│   │       ├── legal-analysis.md       ← third-party comparison of the two
│   │       └── CLAUDE.md               ← context for legal review sessions
│   └── website-legal-pages/            ← DO NOT MODIFY — legal pages
└── classic-motor-market/            ← Next.js application (all code lives here)
```

**All commands run from `classic-motor-market/`.**

---

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Framework | Next.js (App Router) + TypeScript | Server Components throughout |
| Database | PostgreSQL via Prisma 6 | Neon or Supabase for hosting |
| Auth | NextAuth v5 (Auth.js) | JWT strategy, credentials + Google + Facebook |
| Payments | Stripe v20 | Checkout Sessions + webhooks |
| Media | Cloudflare Images | Store only `imageId`; Cloudflare Stream for video (optional) |
| Email | Resend | Contact-seller relay only |
| UI | Tailwind CSS v4 + shadcn/ui | Radix primitives, react-hook-form, Zod |
| Hosting | Vercel | |
| Optional | Vercel KV / Upstash Redis (caching), Sentry (monitoring) | Not yet implemented |

**Key package versions** (from `package.json`):
- `next`: 16.0.10, `react`: 19.2.0
- `prisma`: 6.19.0, `@prisma/client`: 6.19.0
- `next-auth`: 5.0.0-beta.30
- `stripe`: 20.0.0
- `resend`: 6.5.2
- `zod`: 4.1.13, `react-hook-form`: 7.67.0
- `@dnd-kit/core` + `@dnd-kit/sortable` for image drag-reorder

---

## Environment Variables

Required in `.env.local` (inside `classic-motor-market/`):

```
DATABASE_URL=                          # PostgreSQL connection string (Neon: include sslmode=require)
AUTH_SECRET=                           # JWT signing secret (also accepted as NEXTAUTH_SECRET)
AUTH_URL=                              # e.g. http://localhost:3000 (also NEXTAUTH_URL)
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=                  # also accepted as CLOUDFLARE_IMAGES_TOKEN
NEXT_PUBLIC_CLOUDFLARE_ACCOUNT_HASH=   # also accepted as CLOUDFLARE_ACCOUNT_HASH
RESEND_API_KEY=                        # optional; falls back to console.log demo mode
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_APP_URL=                   # base URL used for Stripe redirect URLs
# Optional OAuth:
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=
AUTH_FACEBOOK_ID=
AUTH_FACEBOOK_SECRET=
```

**Vercel-specific:** also set `AUTH_TRUST_HOST=true` — required for Auth.js to work on Vercel.

---

## Application Structure (`classic-motor-market/`)

### `app/` — Pages & Routes

```
app/
├── layout.tsx              # Root layout — wraps everything in <DisclaimerGate>
├── page.tsx                # Home page (hero, featured vehicles, membership CTA)
├── globals.css             # Tailwind base + CSS custom properties (color tokens)
├── login/page.tsx
├── register/page.tsx
├── contact/page.tsx
├── privacy/page.tsx
├── terms/page.tsx
├── listings/
│   ├── page.tsx            # Browse all active listings + sold section
│   └── [slug]/page.tsx     # Vehicle detail — slug = {year}-{make}-{model}-{publicId}
├── sell/
│   ├── page.tsx            # Create new listing (renders ListingWizard)
│   └── [id]/page.tsx       # Edit existing listing
├── account/
│   ├── layout.tsx          # Sidebar nav layout (members only)
│   ├── page.tsx            # Account dashboard
│   ├── listings/page.tsx   # My listings table
│   ├── watchlist/page.tsx  # Saved vehicles
│   ├── billing/page.tsx    # Membership management
│   └── settings/page.tsx   # Profile settings
├── admin/
│   ├── layout.tsx          # Admin-only guard
│   ├── page.tsx            # Admin home
│   ├── listings/page.tsx   # All listings management table
│   ├── dashboard/page.tsx  # Analytics (placeholder)
│   └── users/page.tsx      # User management
├── actions/
│   ├── auth.ts             # registerAction, loginAction
│   ├── listing.ts          # createListing, updateListingStatus, updatePublishFeeStatus, deleteListing
│   ├── contact.ts          # contactSeller (Resend relay)
│   ├── admin.ts            # toggleFeatured, updateUserRole, deleteUser
│   ├── watchlist.ts        # toggleWatchlist
│   ├── cleanup.ts          # DB cleanup utilities
│   └── report.ts           # reportListing
└── api/
    ├── auth/[...nextauth]/route.ts   # NextAuth handlers
    ├── upload/route.ts               # POST/DELETE Cloudflare image upload
    └── stripe/checkout/route.ts      # Stripe checkout session (placeholder)
```

### `components/`

```
components/
├── ui/                     # shadcn/ui components (button, input, form, card, dialog, etc.)
│   ├── image-upload.tsx    # Drag-drop image uploader with dnd-kit reordering
│   └── video-upload.tsx    # Video upload (placeholder)
├── layout/
│   ├── header.tsx          # Main nav header
│   ├── footer.tsx
│   ├── main-nav.tsx        # Desktop navigation
│   ├── mobile-nav.tsx
│   ├── user-menu.tsx       # Authenticated user dropdown
│   └── site-container.tsx  # Max-width wrapper
├── auth/
│   ├── login-form.tsx
│   └── register-form.tsx
├── listing/
│   ├── listing-wizard.tsx       # 5-step listing creation/edit form
│   ├── listing-card.tsx         # Browse page card
│   ├── listing-gallery.tsx      # Lightbox image gallery
│   ├── listing-actions.tsx      # Edit/delete/publish controls
│   ├── member-listings-banner.tsx  # Full-width brand-dark banner ("MEMBER LISTINGS")
│   ├── contact-seller-dialog.tsx
│   ├── watchlist-button.tsx
│   ├── share-button.tsx
│   └── report-button.tsx
├── admin/
│   ├── featured-toggle.tsx
│   ├── cleanup-button.tsx
│   └── user-actions.tsx
├── billing/
│   └── upgrade-button.tsx       # Stripe checkout trigger
└── legal/
    └── disclaimer-gate.tsx      # Dev disclaimer modal (localStorage-gated)
```

### `lib/`

```
lib/
├── prisma.ts               # Prisma client singleton
├── stripe.ts               # Stripe client init
├── utils.ts                # cn(), generateListingSlug(), formatCurrency(), getCloudflareImageUrl()
├── listing-utils.ts        # isInEarlyAccess(), shouldShowAsPlaceholder(), createPlaceholderListing()
└── validations/
    └── listing.ts          # Zod schema for listing form
```

### `prisma/`

```
prisma/
├── schema.prisma           # Authoritative DB schema
└── migrations/             # Migration history
```

### `scripts/`

```
scripts/
├── import-bulk-vehicles.ts    # Seed DB from /bulk-import-vehicles/
├── bulk-import-vehicles.js    # JS version of above
├── wipe-listings-and-images.ts
├── test-db.js
├── check-listings.js
└── check-users.js
```

---

## Database Schema

### Enums

```prisma
enum ListingStatus        { active draft sold }
enum TitleStatus          { clean salvage stolen lien flood }
enum MembershipStatus     { none member expiredMember }
enum MembershipPaymentStatus { unpaid placeholder_confirmed paid }
enum MediaType            { image video }
enum MediaProvider        { cloudflare_images cloudflare_stream }
enum ConditionGrade       { show_car driver it_runs project }
enum PublishFeeMethod     { placeholder_checkbox stripe }
```

### Models

**User**
- `id` Int PK, `publicId` UUID unique
- `username` unique (shown publicly, never email)
- `email` unique, `passwordHash`
- `name`, `phone`, `image`, `emailVerified`
- `stripeCustomerId`
- `membershipStatus` (none/member/expiredMember)
- `membershipPaymentStatus`
- `membershipPaidAt`, `membershipExpiresAt` (1 year from signup)
- `isAdmin` Boolean
- Relations: listings, savedListings, accounts, sessions

**Listing**
- `id` Int PK, `publicId` String unique (used in slugs)
- `sellerId` → User
- `listingStatus` (draft/active/sold)
- `publishedAt`, `featured`, `publishFeePaid`, `publishFeePaidAt`, `publishFeeMethod`
- Basic: `year`, `make`, `model`, `vehicleIdentifier`, `mileage`, `location`
- Specs: `engine`, `transmission`, `exteriorColor`, `interiorColorMaterial`, `askingPrice`
- Narrative: `optionsAndFeatures`, `modifications`
- Condition: `conditionGrade`, `vehicleHistory`, `maintenanceHistory`, `titleStatus`, `carfaxAvailable`
- Relations: media, savedListings

**ListingMedia**
- `id` Int PK, `listingId` → Listing
- `type` (image/video), `provider` (cloudflare_images/cloudflare_stream)
- `providerId` — Cloudflare ID (this is what we store, not URLs)
- `sortOrder`, `isCover` Boolean, `altText`

**SavedListing** — join table: userId + listingId

**Auth.js tables**: Account, Session, VerificationToken

---

## Key Business Logic

### Membership & Access Control

| Role | Access |
|------|--------|
| Public (not logged in) | Browse listings after 10-min early access window, view detail pages, no VIN, no seller contact |
| Member | Everything + full VIN, contact sellers, watchlist, list vehicles, early access window |
| Admin | Everything + admin dashboard, manage all listings/users, feature toggle |

**Route protection:**
- `/admin/*` — `isAdmin` check in `app/admin/layout.tsx`
- `/account/*`, `/sell/*` — session check, redirect to `/login`
- All server actions verify session and ownership before mutating

### Early Access (10-Minute Window)

```
lib/listing-utils.ts:
- isInEarlyAccess(listing) → true if createdAt > NOW - 10min
- shouldShowAsPlaceholder(listing, session) → true if early access AND not a member
- createPlaceholderListing(listing) → replaces data with "New Arrival" / "Member Exclusive"
```

Non-members browsing listings within 10 minutes of creation see a placeholder card. After 10 minutes, the full listing is visible to everyone.

> **Note:** The intended early access window is **48 hours**. It is currently set to **10 minutes** for development/testing. When going to production, update the threshold in `lib/listing-utils.ts`.

### Listing Slug Format

```
/listings/{year}-{make}-{model}-{publicId}
```

Generated by `generateListingSlug()` in `lib/utils.ts`. The `publicId` is a cuid2 short ID stored on the Listing model.

### Image Handling

- Upload via `POST /api/upload` → Cloudflare Images API → returns `{ id, url }`
- Store only `providerId` (Cloudflare image ID) in `listing_media` table, never full URLs
- Render via `getCloudflareImageUrl(imageId, variant)` → `https://imagedelivery.net/{ACCOUNT_HASH}/{imageId}/{variant}`
- Default variant: `"public"`
- Max 50 images per listing; first image (`sortOrder=0`) becomes `isCover=true`
- Delete via `DELETE /api/upload` with `{ id }` body → calls Cloudflare delete API

### Email Relay (Contact Seller)

`contactSeller()` action in `app/actions/contact.ts`:
1. Sends email **to the seller** with buyer's message
2. Sets `reply-to` as buyer's email
3. Seller's email is never exposed to buyer — they reply via email client
4. If `RESEND_API_KEY` not set, falls back to `console.log` (demo mode)

### Payment Flow (Current State)

**Membership ($49/year):**
- Collected at signup via placeholder checkbox
- Sets `membershipStatus = 'member'`, `membershipPaymentStatus = 'placeholder_confirmed'`
- Sets `membershipExpiresAt = NOW + 1 year`
- TODO: Wire to Stripe Checkout Session

**Listing Publish Fee ($20, after first free listing):**
- First listing included with membership
- Currently gated by a checkbox in Step 5 of the wizard → sets `publishFeePaid = true`
- TODO: Wire to Stripe PaymentIntents before publish action completes

**Stripe endpoint:** `POST /api/stripe/checkout` — currently a placeholder skeleton.

---

## 5-Step Listing Wizard

### Step 1: Basic Info
Fields (all single-column, no spinner arrows on number inputs):
- `year` (int, 1900–2100, required)
- `make` (string, required)
- `model` (string, required)
- `vehicleIdentifier` — VIN / WMI / Chassis Number (string, allow European formats, required)
- `location` (free-form string, e.g. "Austin, TX" or "Paris, FR", required)
- `mileage` (int ≥ 0, required)
- `engine` (string, optional)
- `transmission` (string, optional)
- `exteriorColor` (string, required)
- `interiorColorMaterial` (string, required)
- `askingPrice` (int, stored in USD cents, required)

### Step 2: Options, Features & Modifications
- `optionsAndFeatures` — "What options and special features does this vehicle have?" (long-form textarea)
- `modifications` — "Is the vehicle stock or does it have any modifications?" (long-form textarea)

### Step 3: Condition & History
- `conditionGrade` (radio: show_car / driver / it_runs / project, required)
- `vehicleHistory` — "What is the history of the vehicle?" (textarea, required)
- `maintenanceHistory` — "What is known about the maintenance and/or restoration history?" (textarea, required)
- `titleStatus` (optional select: clean / salvage / stolen / lien / flood)
- `carfaxAvailable` (boolean checkbox, optional)

### Step 4: Images
- Drag-and-drop with dnd-kit
- Max 50 photos
- In-place drag handles to reorder → updates `listing_media.sortOrder`
- First photo becomes hero (`isCover = true`)
- At least 1 image required to publish

### Step 5: Review & Publish
- Read-only preview of the full listing
- `Save Draft` → `listingStatus = 'draft'`
- `Publish & Pay` → requires `publishFeeConfirmed` checkbox → sets `listingStatus = 'active'`, `publishFeePaid = true`
- Checkbox unchecked = CTA disabled + helper text: "Publishing requires confirming payment. For now, check the box once you've collected the fee manually."

---

## Zod Validation Schema (`lib/validations/listing.ts`)

```typescript
{
  id?: number                    // edit mode only
  year: number                   // 1900–2100
  make, model, vehicleIdentifier: string
  mileage: number                // ≥ 0
  location: string               // 2+ chars
  exteriorColor, interiorColorMaterial: string
  engine?, transmission?: string
  askingPrice: number            // ≥ 1
  optionsAndFeatures?, modifications?: string
  conditionGrade: 'show_car' | 'driver' | 'it_runs' | 'project'
  vehicleHistory, maintenanceHistory: string
  titleStatus?: 'clean' | 'salvage' | 'stolen' | 'lien' | 'flood'
  carfaxAvailable: boolean       // default false
  images: string[]               // 1+ Cloudflare image IDs required
  publishFeeConfirmed?: boolean  // default false
}
```

---

## Auth Schema (`app/actions/auth.ts`)

```typescript
// Register
{
  name: string               // 2+ chars
  username: string           // 3–20 chars, [a-zA-Z0-9._-]
  email: string              // valid email
  password: string           // 6+ chars
  confirmPassword: string    // must match password
  termsAccepted: boolean     // must be true
  membershipPaymentConfirmed: boolean  // must be true
}
```

---

## Design System

### Color Tokens (defined in `globals.css`)

| Token | Usage |
|-------|-------|
| `brand-dark` | Deep navy — primary brand color |
| `brand-gold` | Metallic gold — accent |
| `page` / `page-alt` | Page backgrounds |
| `card` | Card backgrounds |
| `text-main` / `text-muted` | Typography |
| `border-soft` / `border-strong` | Borders |

### Typography

- Display headings: **Abril Fatface**
- Body: **Roboto Slab** (`--font-roboto-slab`)
- Serif prices/labels: Custom variant

### Component Library

All UI components come from `shadcn/ui` (Radix + Tailwind). Do not build custom primitives for things shadcn already covers.

### Responsive Breakpoints

Standard Tailwind: `sm`, `md`, `lg`. Mobile-first. Tables collapse to cards on mobile.

---

## API Routes

| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET/POST | `/api/auth/[...nextauth]` | — | NextAuth handlers |
| POST | `/api/upload` | Session required | Upload image to Cloudflare |
| DELETE | `/api/upload` | Session required | Delete image from Cloudflare by ID |
| POST | `/api/stripe/checkout` | Session required | Create Stripe checkout session (placeholder) |

---

## Server Actions

### `app/actions/auth.ts`
- `registerAction(data)` → creates User, sets membership, auto-signs in, redirects to `/`
- `loginAction(data)` → credentials sign in, redirects to `/`

### `app/actions/listing.ts`
- `createListing(data, intent)` → intent = `"draft"` | `"publish"`; handles image reconciliation (delete removed, re-create sorted), ownership check
- `updateListingStatus(id, status)` → toggle active/sold/draft
- `updatePublishFeeStatus(id, paid)` → toggle publishFeePaid
- `deleteListing(id)` → delete listing + all Cloudflare images
- `deleteCloudflareImage(imageId)` → internal helper

### `app/actions/contact.ts`
- `contactSeller(listingId, { name, email, phone, message })` → Resend relay

### `app/actions/admin.ts`
- `toggleFeatured(listingId)` → flip featured boolean
- `updateUserRole(userId, isAdmin)` → promote/demote
- `deleteUser(userId)` → delete with guards (can't delete self, can't delete last admin)

### `app/actions/watchlist.ts`
- `toggleWatchlist(listingId)` → upsert/delete SavedListing

---

## Deployment (Vercel)

**Repo:** `atreyusutton/classic-motor-market`
**Root Directory setting in Vercel:** `classic-motor-market`
**Build Command:** `npm run build`
**Node runtime:** 18 or 20

**First deploy — apply schema to Neon:**
```bash
DATABASE_URL=... npx prisma db push
```

**Bulk import to production Neon:**
```bash
DATABASE_URL=... \
CLOUDFLARE_ACCOUNT_ID=... \
CLOUDFLARE_IMAGES_TOKEN=... \
npx tsx scripts/import-bulk-vehicles.ts --run --seller-email="seller@example.com"
```
- Omit `--run` for a dry run
- Seller must exist in DB first; promote to admin with `node make-admin.js`

**Post-deploy checklist:**
- Set `AUTH_URL`/`NEXTAUTH_URL` and `NEXT_PUBLIC_APP_URL` to live domain
- Set `AUTH_TRUST_HOST=true`
- Validate: `/`, `/listings`, `/login`, `/register`, `/sell`, `/account`, `/admin`
- Confirm Cloudflare images render via `imagedelivery.net`
- Confirm Resend sends (or logs "DEMO MODE" if key missing)
- Confirm Stripe checkout uses correct `NEXT_PUBLIC_APP_URL` for redirects

---

## Scripts

Run from `classic-motor-market/` unless noted.

```bash
# Dev server
npm run dev

# Database
npx prisma migrate dev          # run migrations
npx prisma generate             # regenerate client after schema changes
npx prisma studio               # GUI

# Bulk import vehicles (from repo root's bulk-import-vehicles/ dir)
npx ts-node scripts/import-bulk-vehicles.ts --seller-email=test@test.com        # dry run
npx ts-node scripts/import-bulk-vehicles.ts --seller-email=test@test.com --run  # commit

# Wipe listings
npx ts-node scripts/wipe-listings-and-images.ts

# Debug
node scripts/test-db.js
node scripts/check-listings.js
node scripts/check-users.js
```

---

## Navigation & Header States

**Not logged in:** Login | Become a Member | List Your Vehicle

**Logged in (member):** List Your Vehicle | Account dropdown (username, Member badge, Account Settings, Sign Out)

**Logged in (admin):** Same as member + "Admin Dashboard" in main nav

**Logo:** `public/assets/logo.png`
**Hero:** `public/assets/hero.png`

---

## Browse Listings Page Features (Planned/Partially Implemented)

- Filters sidebar: Price Range, Make, Year From/To, Condition (checkboxes), Mileage Min/Max, Transmission
- View toggle: Grid / List
- Results count
- Sold section at bottom (listingStatus = 'sold')
- Pagination
- Search/filter is **not yet implemented** in the current codebase — listing page shows all active listings, newest first

---

## Admin Dashboard Capabilities

- **Listings table**: image + details, price, seller, status badge, publish fee paid, created date
- **Per-listing actions**: View, Edit, Toggle featured, Toggle sold/active, Delete, Override publish fee paid
- **Status badges**: Draft (yellow), Active (green), Sold (red)
- **Users table**: list all users, promote/demote admin, delete user
- **Dashboard analytics**: placeholder, not yet implemented

---

## What's Not Yet Built

| Feature | Status |
|---------|--------|
| Stripe payment for membership | Placeholder checkbox |
| Stripe payment for listing fee | Placeholder checkbox |
| Stripe webhooks updating membership | Skeleton only |
| Search/filter on browse page | Not implemented |
| Video upload (Cloudflare Stream) | Placeholder component |
| Email verification on signup | Not implemented |
| Password reset flow | Not implemented |
| 2FA / additional security | Not implemented |
| Admin analytics dashboard | Placeholder page |
| Username editing in account settings | Not implemented |
| Caching (Redis/KV) | Not implemented |
| Monitoring (Sentry) | Not implemented |

---

## Recent UI Changes (April 2026)

### Member Listings Banner
- `components/listing/member-listings-banner.tsx` — full-viewport-width banner with `bg-brand-dark`, white serif text
- Text: "MEMBER LISTINGS" (large) + "VEHICLES FROM OUR COLLECTORS AND MEMBERS" (smaller below)
- Uses `w-screen` with `left-1/2 -translate-x-1/2` to break out of any container
- Placed on: **home page** (before featured showcases) and **listing detail page** (between gallery and related listings)
- **Not** on the browse/catalog page (`/listings`)

### Listing Detail Page (`/listings/[slug]`)
- Added spacing (`mb-3 sm:mb-4`) under year/make/model title
- Compact top section: `space-y-2` with `pt-6 sm:pt-8 pb-4 sm:pb-6`
- SOLD badge moved to overlay on hero image (top-right red banner) instead of inline text
- Sidebar: year/make/model is now `text-xl sm:text-2xl font-bold`
- Spec rows use `text-sm sm:text-base` for slightly larger text
- Narrative card headings are `text-base sm:text-lg`
- Related listings section separated from gallery by `pt-10 sm:pt-14`

### Home Page Featured Showcases
- Text always on left, photo always on right (removed alternating layout)
- Spec box matches detail page format: Engine, Transmission, Exterior/Interior, Mileage, Location
- Removed: Condition, VIN, Title from featured showcase specs
- Removed: "Member Listings / Hand-picked vehicles" section header + "View the catalogue" link

### Listing Cards
- Year/make/model bumped to `text-2xl`
- Price displayed as `text-2xl font-bold` at bottom
- Mileage/transmission/location combined on one line with `/` separator
- Removed inline "SOLD" text from card title

### Footer
- "Classic Motor Market" text changed from `font-sans` to `font-serif` to match header nav bar

### Legal
- Added Section 23 ("Interim Agreement Acknowledgment") to `cmm-docs/legal/revisions/agreement-essentials.md` — all founders agree to wait for lawyer-drafted operating agreement before going live, for tax purposes

---

## Security Notes

- Passwords hashed with bcryptjs (10 rounds)
- JWT sessions via NextAuth; token stores `user.id`, `username`, `membershipStatus`, `isAdmin`
- All server actions verify session and check ownership before mutations
- Seller email never exposed — relay-only via Resend
- VIN shown as `"****XXXX"` to non-members
- Admin routes protected at both middleware and layout level
- Disclaimer gate prevents access to site until acknowledged (localStorage)
