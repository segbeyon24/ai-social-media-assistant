# Frontend Summary

4.1 Frontend Stack
    Framework: React 18
    Bundler: Vite
    Language: TypeScript
    Styling: TailwindCSS
    State: Lightweight custom stores
    Auth: Supabase client
    Design: Minimalist + customizable



4.2 Frontend Directory Structure

frontend/
└── vite-react/
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── postcss.config.cjs
    │
    └── src/
        ├── main.tsx
        ├── App.tsx
        │
        ├── routes/
        │   └── AppRouter.tsx
        │
        ├── pages/
        │   ├── Home.tsx              ✅
        │   ├── Dashboard.tsx         ✅ (/me)
        │   ├── Login.tsx             ✅
        │   ├── NotFound.tsx          ✅
        │
        ├── components/
        │   ├── layout/
        │   │   └── AppShell.tsx      ✅
        │   │
        │   ├── sidebar/
        │   │   └── Sidebar.tsx       ✅
        │   │
        │   ├── cards/
        │   │   └── MetricCard.tsx    ✅
        │   │
        │   ├── charts/
        │   │   └── EngagementChart.tsx ✅
        │   │
        │   └── theme/
        │       └── ThemeSwitcher.tsx ✅
        │
        ├── state/
        │   ├── auth.ts               ✅
        │   └── theme.ts              ✅
        │
        ├── lib/
        │   ├── supabase.ts           ✅
        │   ├── api.ts                ✅
        │   └── constants.ts          ✅
        │
        ├── styles/
        │   └── themes.ts             ✅
        │
        └── index.css                 ✅



4.3 Frontend Responsibilities
UX & Navigation
    Home → Login → Dashboard
    /me as user control center
    Consistent shell layout

Theming System
    Dark / light / custom palettes
    Token-based design (VSCode-like)
    User-persisted preferences

Analytics Display
    Unified metric cards
    Platform-agnostic charts
    Ready for drill-down

API Integration
    Centralized API client
    Token-aware requests
    Backend-first logic


4.4 Known Frontend Limitations

| Area          | Limitation                       |
| ------------- | -------------------------------- |
| Offline       | No offline caching               |
| Animations    | Minimal micro-interactions       |
| Accessibility | Needs audit                      |
| Error UX      | Backend errors not surfaced well |
| Realtime      | No live updates yet              |


4.5 Frontend Upgrade Paths
    Motion system (Framer Motion)
    Calendar-based scheduler UI
    AI composer workspace
    Realtime analytics (WebSockets)
    Mobile-first responsive refinement


