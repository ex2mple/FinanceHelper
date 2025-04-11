<template>
  <div class="text-white p-4 min-h-screen font-sans">
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
            class="w-[150px] md:w-[180px] !text-sm !bg-gray-700 !border-gray-600"
        />
      </div>
    </div>

        <!-- Сводка (динамическая, с использованием Card и Tailwind для стилей) -->
    <div class="grid grid-cols-2 gap-4 mb-6">
       <!-- Карточка Траты -->
       <Card
          class="!bg-surface-50 dark:!bg-surface-800 !rounded-lg !shadow-none hover:bg-surface-100 dark:hover:bg-surface-700/50 cursor-pointer transition duration-150 overflow-hidden"
          @click="onSummaryClick('expenses')"
          :pt="{ body: { class: '!p-0' }, content: { class: '!p-0' } }"
       >
         <template #content>
          <div class="p-4">
             <div class="text-lg font-semibold text-surface-700 dark:text-surface-0/80 dark:text-red-400">{{ totalExpensesFormatted }}</div>
             <div class="text-sm text-surface-500 dark:text-surface-400">Траты</div>
          </div>
         </template>

       </Card>

       <!-- Карточка Доходы -->
       <Card
          class="!bg-surface-50 dark:!bg-surface-800 !rounded-lg !shadow-none hover:bg-surface-100 dark:hover:bg-surface-700/50 cursor-pointer transition duration-150 overflow-hidden"
          @click="onSummaryClick('income')"
          :pt="{ body: { class: '!p-0' }, content: { class: '!p-0' } }"
       >
         <template #content>
         <div class="p-4">
            <div class="text-lg font-semibold text-green-500 dark:text-green-400">{{ totalIncomeFormatted }}</div>
            <div class="text-sm text-surface-500 dark:text-surface-400">Доходы</div>
         </div>
         </template>
       </Card>
   </div>

    <!-- Список транзакций -->
    <div v-if="Object.keys(groupedTransactions).length > 0" class="space-y-5">
      <Card
          v-for="(transactionsInGroup, dateKey) in groupedTransactions"
          :key="dateKey"
          class="!shadow-none !rounded-lg"
          :pt="{ header: { class: '!p-3 !border-b !border-gray-700' }, body: { class: '!p-0' }, content: { class: '!p-0' } }"
      >
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-base font-semibold text-gray-300">{{ dateKey }}</h2>
            <span class="text-sm text-gray-500 font-medium">{{ calculateDailyTotal(transactionsInGroup) }}</span>
          </div>
        </template>
        <template #content>
          <ul class="divide-y divide-gray-700">
            <li
                v-for="transaction in transactionsInGroup"
                :key="transaction.id"
                class="flex items-center justify-between p-3 hover:bg-gray-700/50 cursor-pointer transition duration-150 ease-in-out"
                @click="onTransactionClick(transaction)"
            >
              <div class="flex items-center overflow-hidden mr-2">
                <!-- Иконка PrimeVue Avatar -->
                <Avatar
                    :image="transaction.iconUrl"
                    :label="!transaction.iconUrl ? transaction.name.charAt(0) : undefined"
                    :class="['!h-10 !w-10 mr-3 flex-shrink-0', getIconBgClass(transaction.category)]"
                    shape="circle"
                />
                <!-- Детали -->
                <div class="overflow-hidden">
                  <div class="font-medium text-sm truncate">{{ transaction.name }}</div>
                  <div class="text-xs text-gray-400 truncate">{{ transaction.category }}</div>
                </div>
              </div>
              <!-- Сумма и доп. инфо -->
              <div class="text-right flex-shrink-0 ml-2">
                <div
                    :class="[
                        'font-semibold text-sm',
                        transaction.amount > 0 ? 'text-green-400' : 'text-white'
                        ]"
                >
                  {{ formatAmount(transaction.amount) }}
                </div>
                <div v-if="transaction.details || transaction.bonus"
                     class="text-xs text-gray-500 mt-0.5 flex justify-end items-center gap-1">
                  <!-- Пример отображения бонусов или деталей -->
<!--                  <Tag v-if="transaction.bonus" :value="`+${transaction.bonus}`" severity="warning"-->
<!--                       class="!text-[10px] !px-1 !py-0"></Tag>-->
<!--                  <span class="truncate">{{ transaction.details }}</span>-->
                </div>
              </div>
            </li>
          </ul>
        </template>
      </Card>
    </div>
    <div v-else class="text-center text-gray-500 mt-10">
      Нет транзакций за выбранный период.
    </div>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Tag from 'primevue/tag';
import Card from 'primevue/card';

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

// Пример данных транзакций (ЗАМЕНИТЕ НА ВАШИ)
const allTransactions = ref([
  {
    id: 1,
    date: '2024-04-11',
    name: 'О!Эскимо',
    category: 'Супермаркеты',
    amount: -120,
    details: 'Основной счет Tinkoff',
    iconUrl: 'https://via.placeholder.com/40/E91E63/FFFFFF?text=O'
  },
  {
    id: 1,
    date: '2024-04-11',
    name: 'О!Эскимо',
    category: 'Супермаркеты',
    amount: -120,
    details: 'Основной счет Tinkoff',
    iconUrl: 'https://via.placeholder.com/40/E91E63/FFFFFF?text=O'
  },
  {id: 2, date: '2024-04-11', name: 'Арсений Д.', category: 'Переводы', amount: 14000, details: 'MasterCard'},
  {id: 3, date: '2024-04-11', name: 'Стрелка', category: 'Транспорт', amount: -72, details: 'Компенсация'},
  {
    id: 4,
    date: '2024-04-09',
    name: 'Вкусно — и точка',
    category: 'Фастфуд',
    amount: -280,
    details: 'Основная',
    bonus: 2,
    iconUrl: 'https://via.placeholder.com/40/FF9800/FFFFFF?text=V'
  },
  {id: 5, date: '2024-04-09', name: 'Стрелка', category: 'Транспорт', amount: -72, details: 'Компенсация'},
  {
    id: 6,
    date: '2024-04-09',
    name: 'Московский метрополитен',
    category: 'Местный транспорт',
    amount: -595,
    details: 'Основной счет Tinkoff'
  },
  {
    id: 7,
    date: '2024-04-07',
    name: 'Пятерочка',
    category: 'Супермаркеты',
    amount: -520,
    iconUrl: 'https://via.placeholder.com/40/4CAF50/FFFFFF?text=P'
  },
  {id: 8, date: '2024-04-07', name: 'Зарплата', category: 'Доходы', amount: 51300, details: 'ООО Ромашка'},
  {id: 9, date: '2024-03-25', name: 'Яндекс.Такси', category: 'Транспорт', amount: -350},
  {id: 10, date: '2024-03-15', name: 'Перевод маме', category: 'Переводы', amount: -5000},
  // ... добавьте больше транзакций за разные месяцы
]);

// --- Вспомогательные функции ---

const formatAmount = (amount) => {
  const sign = amount > 0 ? '+' : '';
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

// Получение CSS класса для фона иконки
const getIconBgClass = (category) => {
  const colors = {
    'Супермаркеты': '!bg-pink-600',
    'Переводы': '!bg-yellow-500 !text-gray-900', // Пример с темным текстом
    'Транспорт': '!bg-blue-600',
    'Фастфуд': '!bg-orange-500',
    'Местный транспорт': '!bg-red-700',
    'Доходы': '!bg-emerald-500',
  };
  return colors[category] || '!bg-gray-600'; // Цвет по умолчанию
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
  console.log("Clicked transaction:", transaction);
  // Здесь можно открыть модальное окно, перейти на другую страницу и т.д.
  alert(`Клик по транзакции: ${transaction.name} (${formatAmount(transaction.amount)})`);
}

// --- Фильтрация и Группировка ---

// 1. Фильтруем по выбранному месяцу
const filteredTransactions = computed(() => {
  if (selectedMonth.value === null) { // Если выбрано "Все месяцы"
    return allTransactions.value;
  }
  return allTransactions.value.filter(tx => {
    const txDate = new Date(tx.date);
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
  const sortedTransactions = [...filteredTransactions.value].sort((a, b) => new Date(b.date) - new Date(a.date));

  sortedTransactions.forEach(transaction => {
    const dateKey = formatDateGroup(transaction.date);
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(transaction);
  });
  return groups;
});

</script>

<style>
/* Глобальные стили для кастомизации PrimeVue, если нужно */
/* Например, чтобы Dropdown лучше вписывался в темную тему */
.p-dropdown {
  background: #374151; /* bg-gray-700 */
  border: 1px solid #4b5563; /* border-gray-600 */
}

.p-dropdown .p-dropdown-label {
  color: #d1d5db; /* text-gray-300 */
}

.p-dropdown .p-dropdown-trigger .p-icon {
  color: #9ca3af; /* text-gray-400 */
}

.p-dropdown-panel {
  background: #1f2937; /* bg-gray-800 */
  border: 1px solid #4b5563; /* border-gray-600 */
}

.p-dropdown-item {
  color: #d1d5db; /* text-gray-300 */
}

.p-dropdown-item:hover {
  background: #374151; /* bg-gray-700 */
}

.p-dropdown-item.p-highlight {
  background: #1d4ed8; /* bg-blue-700 */
  color: white;
}

/* Стили для Card */
.p-card .p-card-content {
  padding: 0 !important; /* Убираем лишние паддинги у контента карты */
}

.p-card .p-card-body {
  padding: 0 !important; /* Убираем лишние паддинги у тела карты */
}

/* Убираем стандартные маркеры списка */
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
</style>