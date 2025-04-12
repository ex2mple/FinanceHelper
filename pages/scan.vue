<template>
    <div class="h-full mt-4 flex flex-col items-center justify-center relative">
      <Toast />
      <div class="w-full h-full md:w-auto md:h-auto md:max-w-lg md:mx-auto md:shadow-2xl md:rounded-2xl md:p-8">
        <h2 class="text-3xl font-extrabold text-center mb-6">Сканер QR-кода</h2>
        <div class="relative w-full h-full md:w-auto md:h-auto">
          <video ref="videoRef" class="w-full h-full md:rounded-xl md:shadow-lg" autoplay muted playsinline></video>
          <div class="absolute inset-0 border-4 border-dashed animate-pulse md:rounded-xl pointer-events-none"></div>
        </div>
        <p class="mt-4 text-center text-gray-600">Направьте камеру на QR-код</p>
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