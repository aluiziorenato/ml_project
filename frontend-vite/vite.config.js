import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { viteMockServe } from 'vite-plugin-mock';

export default defineConfig({
  plugins: [
    react(),
    viteMockServe({
      mockPath: 'mock',
    }),
  ],
  server: {
    port: 3002,
    proxy: {
      '/detector-tendencias': 'http://localhost:8000'
    }
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
