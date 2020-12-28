export const production = 'PRODUCTION';
export const staging = 'STAGING';
export const development = 'DEVELOPMENT';

interface ThemeDefinition {
  [key: string]: string;
}

interface ThemesType {
  [key: string]: ThemeDefinition;
}

const ikemTheme: ThemeDefinition = {
  'primary-color': '#e2001a',
  'logo-background-image': 'url("../../../assets/img/logo_ikem.svg")',
  'logo-background-size': 'contain',
  'logo-width': '57px',
  'logo-height': '100%'
};

const stagingTheme: ThemeDefinition = {
  'primary-color': '#2D4496',
  'logo-background-image': 'url("../../../assets/img/logo_mild_blue.svg")',
  'logo-background-size': 'contain',
  'logo-width': '140px',
  'logo-height': '100%'
};

export const theme: ThemesType = {
  PRODUCTION: ikemTheme,
  STAGING: stagingTheme,
  DEVELOPMENT: ikemTheme
};
