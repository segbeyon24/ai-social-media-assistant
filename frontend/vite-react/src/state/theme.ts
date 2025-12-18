const THEME_KEY = 'lean_social_theme'

export function getTheme(){
  return localStorage.getItem(THEME_KEY) || 'light'
}

export function setTheme(t:string){
  localStorage.setItem(THEME_KEY, t)
}
