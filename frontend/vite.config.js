import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/jira-cards/',
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/jira-cards/api': {
        target: 'http://127.0.0.1:8000',
        rewrite: (path) => path.replace(/^\/jira-cards\/api/, '/api'),
      },
      '/health': 'http://127.0.0.1:8000',
    },
  },
});
