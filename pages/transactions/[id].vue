<script setup lang="ts">
import {ref, onMounted, computed} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import instance from '~/axiosinstance'; // Ваш axios инстанс
import Card from 'primevue/card';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
// import Tag from 'primevue/tag'; // Можно использовать Tag, но сделаем вручную для точного стиля

const route = useRoute();
const router = useRouter();

// Типизация для объекта транзакции (желательно вынести в отдельный файл types.ts)
interface Category {
  id: number;
  name: string;
  color: string;
  mcc?: string | number; // Добавляем опциональный MCC код
}

interface Transaction {
  id: number;
  title: string;
  amount: number;
  datetime: string; // Или Date, если вы парсите дату
  category: Category;
  // Другие поля, если они есть...
}

const transactionData = ref<Transaction | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// --- Загрузка данных ---
onMounted(async () => {
  try {
    isLoading.value = true;
    error.value = null;
    const response = await instance.get<Transaction>('/transactions/' + route.params.id);
    transactionData.value = response.data;
  } catch (err) {
    console.error("Ошибка загрузки транзакции:", err);
    error.value = "Не удалось загрузить данные транзакции.";
    // Можно добавить обработку ошибок, например, показ Toast
  } finally {
    isLoading.value = false;
  }
});

// --- Вспомогательные функции ---

// Форматирование суммы (как в index.vue, но без знака + для доходов, т.к. тут одна транзакция)
const formatAmount = (amount: number): string => {
  const sign = amount < 0 ? '-' : '+'; // Сохраняем знак
  const formatted = Math.abs(amount).toLocaleString('ru-RU');
  return `${sign}${formatted} ₽`;
};

// Форматирование даты и времени под скриншот ("12 апреля, 21:05")
const formatDateTime = (dateString: string): string => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    const datePart = date.toLocaleDateString('ru-RU', {day: 'numeric', month: 'long'});
    const timePart = date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
    return `${datePart}, ${timePart}`;
  } catch (e) {
    console.error("Ошибка форматирования даты:", e);
    return 'Неверная дата';
  }
};

// Вычисляемые свойства для удобства использования в шаблоне
const formattedAmount = computed(() => {
  return transactionData.value ? formatAmount(transactionData.value.amount) : '';
});

const formattedDateTime = computed(() => {
  return transactionData.value ? formatDateTime(transactionData.value.datetime) : '';
});

const amountColorClass = computed(() => {
  if (!transactionData.value) return '';
  return transactionData.value.amount < 0 ? 'text-red-500 dark:text-red-400' : 'text-green-500 dark:text-green-400';
});

// --- Обработчики событий ---
const goBack = () => {
  router.back(); // Простой способ вернуться назад
};

const onEditClick = () => {
  // TODO: Реализовать логику редактирования
  alert('Редактирование транзакции (не реализовано)');
  // router.push(`/transactions/${transactionData.value?.id}/edit`);
};

</script>

<template>
  <Toast position="top-right"/>
  <div class="flex justify-center items-start min-h-screen p-4 bg-surface-ground">
    <!-- Карточка транзакции -->
    <Card v-if="!isLoading && transactionData" class="w-full max-w-[450px] shadow-lg border-0 animate-fadein">
      <!-- Заголовок Карточки (Шапка с кнопкой назад и датой) -->
      <template #title>
        <div class="flex items-center justify-between mb-1">
          <Button
              icon="pi pi-arrow-left"
              class="p-button-rounded p-button-text -ml-2"
              @click="goBack"
              aria-label="Назад"
          />
          <span class="text-lg font-semibold text-color-secondary">{{ formattedDateTime }}</span>
          <Button
                icon="pi pi-pencil"
                class="p-button-rounded p-button-text -ml-2"
                @click="onEditClick"
                aria-label="Редактировать категорию"
            />
<!--          <div class="w-8"></div> &lt;!&ndash; Пустой div для выравнивания &ndash;&gt;-->
        </div>
      </template>

      <!-- Содержимое Карточки -->
      <template #content>
        <div class="flex flex-col items-center text-center">
          <!-- Большая иконка/аватар -->
          <Avatar
              :label="transactionData.title ? transactionData.title[0].toUpperCase() : '?'"
              :style="{ backgroundColor: transactionData.category?.color || '#cccccc' }"
              class="h-20 w-20 text-3xl mb-4"
              shape="circle"
          />

          <!-- Название транзакции -->
          <h2 class="text-2xl font-semibold mb-2">{{ transactionData.title }}</h2>

          <!-- Блок с категорией и MCC (стилизован под тег/чип) -->
          <div
              class="inline-flex items-center gap-2 px-3 py-1 bg-surface-100 dark:bg-surface-700 rounded-full text-sm mb-6">
            <span class="font-medium">{{ transactionData.category?.name || 'Без категории' }}</span>
          </div>

          <!-- Сумма транзакции -->
          <div class="text-4xl font-bold" :class="amountColorClass">
            {{ formattedAmount }}
          </div>

          <!-- TODO: Можно добавить кнопку "Редактировать транзакцию" или другие детали -->
          <!--
          <Button label="Редактировать" icon="pi pi-pencil" class="p-button-outlined mt-6" @click="onEditClick" />
          -->
        </div>
      </template>
    </Card>

    <!-- Состояние загрузки -->
    <div v-else-if="isLoading" class="text-center mt-10">
      <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
      <p class="mt-2 text-color-secondary">Загрузка данных...</p>
    </div>

    <!-- Состояние ошибки -->
    <div v-else-if="error" class="text-center mt-10 text-red-500">
      <i class="pi pi-exclamation-triangle text-3xl mb-2"></i>
      <p>{{ error }}</p>
      <Button label="Попробовать снова" icon="pi pi-refresh" class="p-button-text mt-2" @click="onMounted"/>
      <Button label="На главную" icon="pi pi-home" class="p-button-text mt-2" @click="$router.push('/')"/>
    </div>
  </div>
</template>

<style scoped>
/* Дополнительные стили, если Tailwind и PrimeVue недостаточно */
.animate-fadein {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Уменьшаем размер кнопки редактирования категории */
.p-button-sm {
  width: 1.7rem !important;
  height: 1.7rem !important;
}

.p-button-sm .p-icon {
  font-size: 0.8rem !important;
}

</style>