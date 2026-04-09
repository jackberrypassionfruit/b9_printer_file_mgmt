
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
    plugins: [
        tailwindcss(),
    ],
    build: {
        // Write output directly into Django's static folder
        outDir: resolve(__dirname, '../static/dist'),
        emptyOutDir: true,
        rollupOptions: {
            input: resolve(__dirname, 'src/main.js'),
            output: {
                // Predictable filenames — no content hashes
                // This keeps your template <script> tags stable
                entryFileNames: 'main.js',
                chunkFileNames: 'main.js',
                assetFileNames: 'main.css',
            },
        },
    },
})