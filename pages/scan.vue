<template>
    <div class="h-[90vh] w-full flex flex-col items-center justify-center relative">
      <Toast />
      <div class="w-[90%] h-[90%] max-w-xl max-h-[80vh] flex flex-col md:w-auto md:h-auto md:max-w-lg md:mx-auto md:shadow-2xl md:rounded-2xl md:p-8">
        <h2 class="text-2xl md:text-3xl font-extrabold text-center mb-4 md:mb-6">Сканер QR-кода</h2>
        <div class="relative flex-grow w-full h-full md:w-auto md:h-auto">
          <video ref="videoRef" class="absolute inset-0 object-cover w-full h-full md:relative md:rounded-xl md:shadow-lg" autoplay muted playsinline></video>
          <div class="absolute inset-0 border-4 border-dashed animate-pulse md:rounded-xl pointer-events-none"></div>
        </div>
        <p class="mt-3 text-center text-gray-600 md:mt-4">Направьте камеру на QR-код</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import QrScanner from 'qr-scanner';
  import { useRouter } from 'vue-router';
  import { useToast } from 'primevue/usetoast';
  
  const videoRef = ref(null)
  let qrScanner = null
  const router = useRouter()
  const toast = useToast()
  
  const onScanSuccess = (result) => {
    toast.add({ severity: 'success', summary: 'Успех!', detail: 'QR код распознан', life: 3000 })
    qrScanner.stop()
  }
  
  const handleError = (err) => {
    console.error('Ошибка сканера:', err)
    toast.add({ severity: 'error', summary: 'Ошибка', detail: err.message || 'Не удалось запустить сканер', life: 3000 })
  }
  
  onMounted(async () => {
    try {
      if (!videoRef.value) {
        throw new Error('Видео элемент не найден')
      }
      qrScanner = new QrScanner(videoRef.value, result => {
        onScanSuccess(result)
      }, {
        onDecodeError: error => {
          // Можно раскомментировать следующую строку для показа ошибок декодирования (обычно много шума)
          // handleError(error)
        },
        highlightScanRegion: true,
        highlightCodeOutline: true,
      })
      await qrScanner.start()
    } catch (err) {
      handleError(err)
    }
  })
  
  onBeforeUnmount(() => {
    if (qrScanner) {
      qrScanner.stop()
    }
  })
  </script>

<style>
@media (max-width: 768px) {
  body {
    margin: 0;
    padding: 0;
    overflow: hidden;
  }
}
</style>