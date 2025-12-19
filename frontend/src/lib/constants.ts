// Centralized constants for LeanSocial frontend

export const APP_NAME = "LeanSocial";

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  DASHBOARD: "/me",
} as const;

export const API_ENDPOINTS = {
  ME: "/me",
  HEALTH: "/health",
} as const;

// Animation timings (ms) – tuned for calm / premium feel
export const MOTION = {
  FAST: 120,
  BASE: 180,
  SLOW: 260,
} as const;

// Layout constants
export const LAYOUT = {
  SIDEBAR_WIDTH: 260,
  SIDEBAR_COLLAPSED_WIDTH: 84,
  HEADER_HEIGHT: 64,
} as const;

// Feature flags (safe to toggle without refactor)
export const FEATURES = {
  ENABLE_ANALYTICS: true,
  ENABLE_THEME_SWITCHER: true,
  ENABLE_SIDEBAR_COLLAPSE: true,
} as const;

// External links
export const LINKS = {
  GITHUB: "https://github.com/",
  SUPPORT: "mailto:support@leansocial.app",
} as const;
