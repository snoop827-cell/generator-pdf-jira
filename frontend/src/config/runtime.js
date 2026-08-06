const browserOrigin = typeof window !== 'undefined'
  ? window.location.origin
  : '';

export const apiBase = `${browserOrigin}/jira-cards`;
