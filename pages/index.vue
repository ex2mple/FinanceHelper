<template>
  <div class="p-4 min-h-screen font-sans">
    <!-- Верхняя панель: Месяц и Фильтры -->
    <div class="flex flex-wrap items-center justify-between gap-2 mb-6">
      <div class="flex items-center gap-2">
        <!-- Выбор месяца -->
        <Dropdown
            v-model="selectedMonth"
            :options="monthOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Выберите месяц"
            class="w-[150px] md:w-[180px]"
        />
      </div>
    </div>

        <!-- Сводка (динамическая, с использованием Card и Tailwind для стилей) -->
    <div class="grid grid-cols-2 gap-4 mb-6">
       <!-- Карточка Траты -->
       <Card
          class="cursor-pointer transition duration-150 overflow-hidden hover-def"
          @click="onSummaryClick('expenses')"
          :pt="{
            root: { class: 'hover:surface-hover' },
            body: { class: 'p-0' },
            content: { class: 'p-0' }
          }"
       >
         <template #content>
          <div class="p-4">
             <div class="text-lg font-semibold text-red-600">{{ totalExpensesFormatted }}</div>
             <div class="text-sm text-color-secondary">Траты</div>
          </div>
         </template>
       </Card>

       <!-- Карточка Доходы -->
       <Card
          class="cursor-pointer transition duration-150 overflow-hidden hover-def"
          @click="onSummaryClick('income')"
          :pt="{
            root: { class: 'hover:surface-hover' },
            body: { class: 'p-0' },
            content: { class: 'p-0' }
          }"
       >
         <template #content>
         <div class="p-4">
            <div class="text-lg font-semibold text-green-600">{{ totalIncomeFormatted }}</div>
            <div class="text-sm text-color-secondary">Доходы</div>
         </div>
         </template>
       </Card>
   </div>

    <!-- Список транзакций -->
    <div v-if="Object.keys(groupedTransactions).length > 0" class="space-y-5">
      <Card
          v-for="(transactionsInGroup, dateKey) in groupedTransactions"
          :key="dateKey"
          :pt="{
            header: { class: 'p-3 border-bottom-1' },
            body: { class: 'p-0' },
            content: { class: 'p-0'}
          }"
      >
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-base font-semibold">{{ dateKey }}</h2>
            <span class="text-sm text-color-secondary font-medium">{{ calculateDailyTotal(transactionsInGroup) }}</span>
          </div>
        </template>
        <template #content>
          <ul class="divide-y-1">
            <li
                v-for="transaction in transactionsInGroup"
                :key="transaction.id"
                class="flex items-center justify-between p-3 cursor-pointer hover-def transition duration-150 ease-in-out"
                @click="onTransactionClick(transaction)"
            >
              <div class="flex items-center overflow-hidden mr-2">
                <!-- Иконка PrimeVue Avatar -->
                <Avatar
                    :label="`${transaction.title[0]}`"
                    :style="`background-color: ${transaction.category.color}`"
                    :class="['h-10 w-10 mr-3 flex-shrink-0']"
                    shape="circle"
                />
                <!-- Детали -->
                <div class="overflow-hidden">
                  <div class="font-medium text-sm truncate">{{ transaction.title }}</div>
                  <div class="text-xs text-color-secondary truncate">{{ transaction.category.name }}</div>
                </div>
              </div>
              <!-- Сумма и доп. инфо -->
              <div class="text-right flex-shrink-0 ml-2">
                <div :class="['font-semibold text-sm']">
                  {{ formatAmount(transaction.amount) }}
                </div>
              </div>
            </li>
          </ul>
        </template>
      </Card>
    </div>
    <div v-else class="text-center text-color-secondary mt-10">
      Нет транзакций за выбранный период.
    </div>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue';
import Dropdown from 'primevue/dropdown';
import Avatar from 'primevue/avatar';
import Card from 'primevue/card';
import instance from "~/axiosinstance";

// --- Данные ---
// Получаем текущий месяц (0-11)
const currentMonth = new Date().getMonth();
const selectedMonth = ref(currentMonth); // Выбранный месяц по умолчанию - текущий

// Опции для выбора месяца
const monthOptions = ref([
  {label: 'Январь', value: 0},
  {label: 'Февраль', value: 1},
  {label: 'Март', value: 2},
  {label: 'Апрель', value: 3}, // Текущий месяц для примера
  {label: 'Май', value: 4},
  {label: 'Июнь', value: 5},
  {label: 'Июль', value: 6},
  {label: 'Август', value: 7},
  {label: 'Сентябрь', value: 8},
  {label: 'Октябрь', value: 9},
  {label: 'Ноябрь', value: 10},
  {label: 'Декабрь', value: 11},
  {label: 'Все месяцы', value: null}, // Опция для сброса фильтра
]);

const allTransactions = ref([]);

onMounted(async () => {
  allTransactions.value = (await instance.get('/transactions/my')).data
})

// --- Вспомогательные функции ---

const formatAmount = (amount) => {
  const sign = amount > 0 ? '+' : '-';
  const formatted = Math.abs(amount).toLocaleString('ru-RU');
  return `${sign}${formatted} ₽`;
};

const formatDateGroup = (dateString) => {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  date.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  yesterday.setHours(0, 0, 0, 0);

  if (date.getTime() === today.getTime()) return 'Сегодня';
  if (date.getTime() === yesterday.getTime()) return 'Вчера';
  return date.toLocaleDateString('ru-RU', {day: 'numeric', month: 'long'});
};


const calculateDailyTotal = (dailyTransactions) => {
  const total = dailyTransactions.reduce((sum, tx) => sum + tx.amount, 0);
  return formatAmount(total);
}

const onSummaryClick = (type) => {
  console.log(`Clicked summary card: ${type}`);
  alert(`Клик по сводке: ${type === 'expenses' ? 'Траты' : 'Доходы'}`);
  // Здесь можно реализовать фильтрацию транзакций по типу (доход/расход)
}

const totalExpenses = computed(() => {
  // Суммируем все отрицательные суммы из отфильтрованных транзакций
  return filteredTransactions.value
      .filter(tx => tx.amount < 0)
      .reduce((sum, tx) => sum + tx.amount, 0);
});

const totalIncome = computed(() => {
  // Суммируем все положительные суммы из отфильтрованных транзакций
  return filteredTransactions.value
      .filter(tx => tx.amount > 0)
      .reduce((sum, tx) => sum + tx.amount, 0);
});

const totalExpensesFormatted = computed(() => {
  const absAmount = Math.abs(totalExpenses.value);
  const formatted = absAmount.toLocaleString('ru-RU'); // Форматируем без знака
  return `${formatted} ₽`; // Добавляем валюту
});

const totalIncomeFormatted = computed(() => {
  // Используем formatAmount, который добавит знак "+"
  return formatAmount(totalIncome.value);
});

// --- Логика кликабельности ---
const onTransactionClick = (transaction) => {
  const router = useRouter()
  router.push('/transactions/' + transaction.id);
}

// --- Фильтрация и Группировка ---

// 1. Фильтруем по выбранному месяцу

const filteredTransactions = computed(() => {
  if (selectedMonth.value === null) { // Если выбрано "Все месяцы"
    return allTransactions.value;
  }
  return allTransactions.value.filter(tx => {
    const txDate = new Date(tx.datetime);
    return txDate.getMonth() === selectedMonth.value;
    // Можно добавить фильтрацию по году, если нужно: && txDate.getFullYear() === нужный_год
  });
});

// 2. Группируем отфильтрованные транзакции
const groupedTransactions = computed(() => {
  const groups = {};
  if (!filteredTransactions.value || filteredTransactions.value.length === 0) {
    return groups;
  }

  // Сортируем отфильтрованные транзакции
  const sortedTransactions = [...filteredTransactions.value].sort((a, b) => new Date(b.datetime) - new Date(a.datetime));

  sortedTransactions.forEach(transaction => {
    const dateKey = formatDateGroup(transaction.datetime);
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(transaction);
  });
  return groups;
});

</script>

<style>
/* Убираем стандартные маркеры списка */
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.hover-def:hover {
  background-color: var(--p-content-hover-background) !important;

}

/* PrimeVue теперь управляет цветами через собственную систему тем */
/* Удалены хардкодированные цветовые стили, так как они теперь берутся из системы тем PrimeVue */
</style>