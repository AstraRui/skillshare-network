export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true,
    },
    host: true, // Обязательно для Docker
    port: 5173,
  },
})