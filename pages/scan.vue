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
  
  <script setup lang="ts">
  import QrScanner from 'qr-scanner';
  import { useRouter } from 'vue-router';
  import { useToast } from 'primevue/usetoast';
  import axios from 'axios';
  import instance from '~/axiosInstance';
  
  // Define proper TypeScript interfaces
  interface CheckData {
    code: number;
    first: number;
    data: {
      json: {
        user: string;
        items: Array<{
          name: string;
          price: number;
          quantity: number;
          sum: number;
          [key: string]: any;
        }>;
        totalSum: number;
        dateTime: string;
        retailPlace: string;
        [key: string]: any;
      };
      html: string;
    };
    request: {
      qrraw: string;
      manual: {
        fn: string;
        fd: string;
        fp: string;
        check_time: string;
        type: string;
        sum: string;
      };
      [key: string]: any;
    };
  }
  
  interface AIResponse {
    response: string;
    [key: string]: any;
  }
  
  const videoRef = ref<HTMLVideoElement | null>(null);
  let qrScanner: QrScanner | null = null;
  const router = useRouter();
  const toast = useToast();
  const loading = ref(false);
  
  const onScanSuccess = (result: QrScanner.ScanResult) => {
    toast.add({ severity: 'success', summary: 'Успех!', detail: 'QR код распознан', life: 3000 });
    getCheckData(result.data);
    qrScanner?.stop();
  }
  
  const handleError = (err: Error) => {
    console.error('Ошибка сканера:', err);
    toast.add({ 
      severity: 'error', 
      summary: 'Ошибка', 
      detail: err.message || 'Не удалось запустить сканер', 
      life: 3000 
    });
  }
  
  const getCheckData = async (query: string) => {
    try {
      loading.value = true;
      const formData = new URLSearchParams();
      // Ideally store this token in an environment variable
      formData.append('token', '32370.Q1CjA0xnV2ICzH6sF');
      formData.append('qrraw', query);
  
      const checkResponse = await axios.post<CheckData>(
        'https://proverkacheka.com/api/v1/check/get', 
        formData, 
        {
          headers: {
            'content-type': 'application/x-www-form-urlencoded',
          }
        }
      );
      
      if (checkResponse.data.code === 1) {
        toast.add({ severity: 'success', summary: 'Успех!', detail: 'Данные чека получены', life: 3000 });
        
        // Извлекаем необходимые данные из чека
        const checkData = checkResponse.data.data.json;
        
        try {
          // Отправляем данные на обработку AI
          const aiResponse = await instance.post<AIResponse>('/ai/ask?model=small', {
            request: `${checkData.items.map(item => item.name).join(', ')}, ${checkData.retailPlace}`,
          });
          
          if (aiResponse.data) {
            // Извлекаем данные из ответа нейросети
            let aiData: { title?: string; category_id?: number } = {};
            
            if (aiResponse.data.response) {
              // Извлекаем JSON из Markdown кода в поле response
              const jsonMatch = aiResponse.data.response.match(/```json\s*\n([\s\S]*?)\n\s*```/);
              if (jsonMatch && jsonMatch[1]) {
                try {
                  // Парсим извлеченную JSON строку
                  aiData = JSON.parse(jsonMatch[1]);
                  console.log('Extracted AI data:', aiData);
                } catch (parseError) {
                  console.error('Failed to parse AI response JSON:', parseError);
                }
              }
            }
            
            // Строим объект для передачи в форму транзакции
            const transactionData = {
              title: aiData.title || checkData.retailPlace || 'Покупка',
              amount: checkData.totalSum / 100, // Конвертируем копейки в рубли
              datetime: new Date(checkData.dateTime),
              type: 'expense', // По умолчанию расход
              category_id: aiData.category_id
            };
            
            // Переходим на страницу добавления транзакции с параметрами
            router.push({
              path: '/transactions/add',
              query: {
                ...transactionData,
                datetime: transactionData.datetime.toISOString()
              }
            });
          }
        } catch (aiError) {
          console.error('Ошибка при обработке AI:', aiError);
          
          // Если AI не сработал, всё равно передаем базовую информацию
          router.push({
            path: '/transactions/add',
            query: {
              title: checkData.retailPlace || 'Покупка',
              amount: checkData.totalSum / 100,
              datetime: new Date(checkData.dateTime).toISOString(),
              type: 'expense'
            }
          });
        }
      } else {
        toast.add({ 
          severity: 'warning', 
          summary: 'Внимание', 
          detail: `Код ответа: ${checkResponse.data.code}`, 
          life: 3000 
        });
      }
    } catch (err) {
      console.error('Ошибка получения данных:', err);
      toast.add({ 
        severity: 'error', 
        summary: 'Ошибка', 
        detail: 'Не удалось получить данные чека', 
        life: 3000 
      });
    } finally {
      loading.value = false;
    }
  }
  
  onMounted(async () => {
    try {
      if (!videoRef.value) {
        throw new Error('Видео элемент не найден');
      }
      qrScanner = new QrScanner(
        videoRef.value, 
        result => {
          onScanSuccess(result);
        }, 
        {
          onDecodeError: error => {
            // Ошибки декодирования происходят постоянно при отсутствии QR кода в кадре
            // handleError(error)
          },
          highlightScanRegion: true,
          highlightCodeOutline: true,
        }
      );
      await qrScanner.start();
    } catch (err) {
      handleError(err instanceof Error ? err : new Error('Неизвестная ошибка'));
    }
  });
  
  onBeforeUnmount(() => {
    if (qrScanner) {
      qrScanner.stop();
      qrScanner.destroy();
    }
  });
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