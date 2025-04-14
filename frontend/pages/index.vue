<template>
  <div class="p-4 min-h-screen font-sans">
    <!-- Toast компонент для уведомлений -->
    <Toast />
    
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
        
        <!-- Кнопка для загрузки CSV файла -->
        <Button 
          icon="pi pi-upload" 
          label="Импорт CSV" 
          severity="secondary" 
          outlined
          @click="openFileUpload"
          class="ml-2"
        />
        
        <!-- Скрытый инпут для выбора файла -->
        <input 
          type="file" 
          ref="fileUploader" 
          accept=".csv" 
          class="hidden" 
          @change="handleFileUpload"
        />
      </div>
    </div>

    <!-- Диаграмма и Сводка -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
       <!-- Карточка Диаграмма Расходов (Full width on MD+) -->
       <Card class="md:col-span-2">
         <template #title>
           <div class="text-base font-semibold">Расходы по категориям</div>
         </template>
         <template #content>
           <!-- Adjusted height for better visibility -->
           <div class="relative h-64 md:h-72 flex items-center justify-center">
             <Chart type="doughnut" v-if="!isLoadingChart && chartData.datasets[0].data.length > 0" :data="chartData" :options="chartOptions" class="h-full w-full" />
             <div v-else-if="isLoadingChart" class="text-sm text-color-secondary">Загрузка диаграммы...</div>
             <div v-else class="text-sm text-color-secondary">Нет данных о расходах за период</div>
           </div>
         </template>
       </Card>

       <!-- Карточка Траты (Half width on MD+) -->
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
             <!-- Optional: Smaller text size if needed -->
             <div class="text-lg font-semibold text-red-600">{{ totalExpensesFormatted }}</div>
             <div class="text-sm text-color-secondary">Траты</div>
          </div>
         </template>
       </Card>

       <!-- Карточка Доходы (Half width on MD+) -->
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
            <!-- Optional: Smaller text size if needed -->
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
import Dropdown from 'primevue/dropdown';
import Avatar from 'primevue/avatar';
import Card from 'primevue/card';
import Toast from 'primevue/toast';
import Chart from 'primevue/chart';
import instance from "~/axiosInstance";
import { useToast } from 'primevue/usetoast';
import { ref, computed, onMounted, watch } from 'vue';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

// --- Данные ---
const currentMonth = new Date().getMonth();
const selectedMonth = ref(currentMonth);
const toast = useToast();

const monthOptions = ref([
  {label: 'Январь', value: 0},
  {label: 'Февраль', value: 1},
  {label: 'Март', value: 2},
  {label: 'Апрель', value: 3},
  {label: 'Май', value: 4},
  {label: 'Июнь', value: 5},
  {label: 'Июль', value: 6},
  {label: 'Август', value: 7},
  {label: 'Сентябрь', value: 8},
  {label: 'Октябрь', value: 9},
  {label: 'Ноябрь', value: 10},
  {label: 'Декабрь', value: 11},
  {label: 'Все месяцы', value: null},
]);

const allTransactions = ref([]);
const groupedChartDataRaw = ref([]);
const isLoadingChart = ref(false);

const fetchChartData = async (month) => {
  isLoadingChart.value = true;
  groupedChartDataRaw.value = [];
  let startDate = null;
  let endDate = null;
  const currentYear = new Date().getFullYear();

  if (month !== null) {
    startDate = new Date(currentYear, month, 1);
    endDate = new Date(currentYear, month + 1, 0, 23, 59, 59, 999);
  }

  try {
    const params = {};
    // Remove trailing 'Z' from ISO string
    if (startDate) params.start_date = startDate.toISOString().slice(0, -1);
    if (endDate) params.end_date = endDate.toISOString().slice(0, -1);

    const response = await instance.get('/transactions/group', { params });
    groupedChartDataRaw.value = response.data;
  } catch (error) {
    console.error('Error fetching grouped chart data:', error);
    if (error.response && error.response.status === 422 && error.response.data?.detail?.[0]?.loc?.includes('transaction_id')) {
       toast.add({ severity: 'error', summary: 'Ошибка API', detail: 'Маршрут /transactions/group конфликтует с другим маршрутом на сервере.', life: 5000 });
    } else {
       toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить данные для диаграммы', life: 3000 });
    }
  } finally {
    isLoadingChart.value = false;
  }
};

onMounted(async () => {
  try {
    allTransactions.value = (await instance.get('/transactions/my')).data;
  } catch (error) {
    console.error('Error fetching initial transactions:', error);
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить транзакции', life: 3000 });
  }
  fetchChartData(selectedMonth.value);
});

watch(selectedMonth, (newMonth) => {
  fetchChartData(newMonth);
});

const formatAmount = (amount) => {
  const sign = amount >= 0 ? '+' : '-';
  const formatted = Math.abs(amount).toLocaleString('ru-RU');
  return `${sign}${formatted} ₽`;
};

const formatExpenseAmount = (amount) => {
  const formatted = Math.abs(amount).toLocaleString('ru-RU');
  return `-${formatted} ₽`;
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
}

const totalExpenses = computed(() => {
  return filteredTransactions.value
      .filter(tx => tx.amount < 0)
      .reduce((sum, tx) => sum + tx.amount, 0);
});

const totalIncome = computed(() => {
  return filteredTransactions.value
      .filter(tx => tx.amount > 0)
      .reduce((sum, tx) => sum + tx.amount, 0);
});

const totalExpensesFormatted = computed(() => {
  const absAmount = Math.abs(totalExpenses.value);
  const formatted = absAmount.toLocaleString('ru-RU');
  return `${formatted} ₽`;
});

const totalIncomeFormatted = computed(() => {
  return formatAmount(totalIncome.value);
});

const onTransactionClick = (transaction) => {
  const router = useRouter()
  router.push('/transactions/' + transaction.id);
}

const filteredTransactions = computed(() => {
  if (selectedMonth.value === null) {
    return allTransactions.value;
  }
  return allTransactions.value.filter(tx => {
    const txDate = new Date(tx.datetime);
    return txDate.getMonth() === selectedMonth.value;
  });
});

const groupedTransactions = computed(() => {
  const groups = {};
  if (!filteredTransactions.value || filteredTransactions.value.length === 0) {
    return groups;
  }

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

const chartData = computed(() => {
  // The new format is ["Category Name", "#ColorHex", -Amount]
  // Filter for expenses (negative amounts) and sort by absolute amount (highest first)
  const expenseData = groupedChartDataRaw.value
    .filter(item => item[2] < 0)
    .map(item => ({
      label: item[0],
      color: item[1],
      amount: Math.abs(item[2])
    }))
    .sort((a, b) => b.amount - a.amount);
    
  // Take only top 5 categories
  const topExpenses = expenseData.slice(0, Math.min(5, expenseData.length));
  
  // If there are more categories, aggregate them into "Other"
  let otherAmount = 0;
  if (expenseData.length > 5) {
    otherAmount = expenseData
      .slice(5)
      .reduce((sum, item) => sum + item.amount, 0);
      
    if (otherAmount > 0) {
      topExpenses.push({
        label: 'Прочие расходы',
        color: '#808080',
        amount: otherAmount
      });
    }
  }

  const labels = topExpenses.map(item => item.label);
  const data = topExpenses.map(item => item.amount);
  const backgroundColors = topExpenses.map(item => item.color);

  return {
    labels: labels,
    datasets: [
      {
        backgroundColor: backgroundColors,
        borderColor: 'white',
        borderWidth: 0,
        data: data
      }
    ]
  };
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
         boxWidth: 20, // Increased size of color squares
         boxHeight: 20, // Added explicit height for squares
         padding: 15,
         font: {
           size: 15 // Increased font size for legend labels
         }
      }
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed !== null) {
            label += context.parsed.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 });
          }
          return label;
        }
      }
    }
  },
  cutout: '60%'
});

const fileUploader = ref(null);

const openFileUpload = () => {
  fileUploader.value.click();
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  console.log(file)
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    toast.add({ severity: 'info', summary: 'Загрузка', detail: 'Загрузка файла...', life: 3000 });

    await instance.post('/transactions/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    allTransactions.value = (await instance.get('/transactions/my')).data;
    await fetchChartData(selectedMonth.value);

    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Файл успешно загружен и данные обновлены', life: 3000 });
    event.target.value = '';
  } catch (error) {
    console.error('Error uploading file:', error);
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Ошибка при загрузке файла: ${error.response?.data?.message || error.message}`,
      life: 5000
    });
  }
};
</script>

<style>
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.hover-def:hover {
  background-color: var(--p-content-hover-background) !important;
}
</style>