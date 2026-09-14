import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Build de production : le bundle est écrit directement dans le dossier
// `static/react/` de Django, puis servi via WhiteNoise (collectstatic).
// Django charge le fichier `main.js` (module ES) dans ses templates.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static/react',
    emptyOutDir: true,
    rollupOptions: {
      input: 'index.html',
      output: {
        entryFileNames: 'main.js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
        inlineDynamicImports: true,
      },
    },
  },
});
