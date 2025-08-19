// Color palette configuration
export const colors = {
  // Professional Blue Palette
  federalBlue: '#03045e',
  marianBlue: '#023e8a',
  honoluluBlue: '#0077b6',
  blueGreen: '#0096c7',
  pacificCyan: '#00b4d8',
  vividSkyBlue: '#48cae4',
  nonPhotoBlue: '#90e0ef',
  nonPhotoBlue2: '#ade8f4',
  lightCyan: '#caf0f8',
  
  // Dark mode colors
  dark: {
    bg: '#0f0f23',
    surface: '#1a1a2e',
    card: '#16213e',
    border: '#2a2a3e',
    text: '#e2e8f0',
    textMuted: '#94a3b8',
    accent: '#6366f1',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  },
  
  // Light mode colors
  light: {
    bg: '#f8fafc',
    surface: '#ffffff',
    card: '#ffffff',
    border: '#e2e8f0',
    text: '#1e293b',
    textMuted: '#64748b',
    accent: '#3b82f6',
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626'
  },
  
  // Neutral colors
  white: '#ffffff',
  gray100: '#f8fafc',
  gray200: '#e2e8f0',
  gray500: '#64748b',
  gray900: '#0f172a'
};

export const gradients = {
  primary: `linear-gradient(135deg, ${colors.federalBlue} 0%, ${colors.marianBlue} 50%, ${colors.honoluluBlue} 100%)`,
  secondary: `linear-gradient(135deg, ${colors.blueGreen} 0%, ${colors.pacificCyan} 50%, ${colors.vividSkyBlue} 100%)`,
  accent: `linear-gradient(135deg, ${colors.vividSkyBlue} 0%, ${colors.nonPhotoBlue} 100%)`,
  light: `linear-gradient(135deg, ${colors.nonPhotoBlue2} 0%, ${colors.lightCyan} 100%)`,
  dark: `linear-gradient(135deg, ${colors.dark.bg} 0%, ${colors.dark.surface} 100%)`
};

export const chartColors = [
  colors.honoluluBlue,
  colors.blueGreen,
  colors.pacificCyan,
  colors.vividSkyBlue,
  colors.nonPhotoBlue,
  colors.marianBlue
];

export const financialColors = {
  profit: '#10b981',
  loss: '#ef4444',
  neutral: '#64748b',
  growth: '#059669',
  decline: '#dc2626'
};