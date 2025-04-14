import Aura from '@primeuix/themes/aura';

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false },
  modules: ['@primevue/nuxt-module', '@nuxtjs/tailwindcss'],
  css: [
    'primeicons/primeicons.css', // Add this line
    // Optionally include the PrimeVue base styles if needed:
    // 'primevue/resources/primevue.min.css'
  ],
  primevue: {
    options: {
      theme: {
        preset: Aura,
      },
    },
  },
})