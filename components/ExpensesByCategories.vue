<template>
  <div class="card">
    <Chart v-if="chartData" type="bar" :data="chartData" :options="chartOptions" class="h-[20rem]"/>
    <div v-else class="flex justify-center items-center h-[30rem]">
      <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
      <span class="ml-2 text-color-secondary">Загрузка данных графика...</span>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import Chart from 'primevue/chart';
import instance from "~/axiosinstance.js"; // Ваш инстанс axios

// --- Реактивные переменные ---
const chartData = ref(null); // Начинаем с null для v-if
const chartOptions = ref(null);
const transactionsData = ref([]);
const expenseCategories = ref([]);

// --- Загрузка и обработка данных при монтировании ---
onMounted(async () => {
  try {
    const response = await instance.get('/transactions/my');
    transactionsData.value = response.data || [];

    expenseCategories.value = getUniqueExpenseCategories(transactionsData.value);

    chartData.value = setChartData();
    chartOptions.value = setChartOptions();

  } catch (error) {
    console.error("Ошибка при подготовке данных для графика:", error);
  }
});

// --- Вспомогательная функция: Получение уникальных категорий расходов ---
const getUniqueExpenseCategories = (transactions) => {
  if (!transactions || transactions.length === 0) {
    return [];
  }
  const categoriesMap = new Map();
  transactions.forEach(tx => {
    if (tx.amount < 0 && tx.category && !categoriesMap.has(tx.category.id)) {
      categoriesMap.set(tx.category.id, {
        id: tx.category.id,
        name: tx.category.name,
        // Используем цвет из категории, если он есть, иначе - стандартный
        color: tx.category.color || '#CCCCCC'
      });
    }
  });
  return Array.from(categoriesMap.values());
};

const setChartData = () => {
  const labels = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

  const monthlySpendingByCategory = {};
  expenseCategories.value.forEach(cat => {
    monthlySpendingByCategory[cat.id] = Array(12).fill(0);
  });

  transactionsData.value.forEach(tx => {
    if (tx.amount < 0 && tx.category) {
      try {
        const transactionDate = new Date(tx.datetime);
        const monthIndex = transactionDate.getMonth();
        const categoryId = tx.category.id;

        if (monthlySpendingByCategory[categoryId] && monthIndex >= 0 && monthIndex < 12) {
          monthlySpendingByCategory[categoryId][monthIndex] += Math.abs(tx.amount);
        }
      } catch (e) {
        console.error("Ошибка обработки даты транзакции:", tx.datetime, e);
      }
    }
  });

  const datasets = expenseCategories.value.map(category => {
    return {
      type: 'bar',
      label: category.name,
      backgroundColor: category.color,
      data: monthlySpendingByCategory[category.id] || Array(12).fill(0)
    };
  });

  return {
    labels: labels,
    datasets: datasets
  };
};

// --- Настройка опций графика (важно: stacked: true) ---
const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--p-text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
  const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

  let overallMaxValue = 0;
// Предполагаем, что chartData.value уже сформирован перед вызовом setChartOptions
  if (chartData.value && chartData.value.datasets) {
    chartData.value.datasets.forEach(dataset => {
      dataset.data.forEach(value => {
        if (value > overallMaxValue) overallMaxValue = value;
      });
    });
    // ПРАВИЛЬНЫЙ расчет maxValue для stacked bar:
    if (chartData.value.labels && chartData.value.datasets.length > 0) {
      const numLabels = chartData.value.labels.length;
      for (let i = 0; i < numLabels; i++) {
        let sumAtIndex = 0;
        chartData.value.datasets.forEach(dataset => {
          if (dataset.data && dataset.data.length > i) {
            sumAtIndex += dataset.data[i];
          }
        });
        if (sumAtIndex > overallMaxValue) {
          overallMaxValue = sumAtIndex;
        }
      }
    }
  }

  const scale = calculateNiceScale(0, overallMaxValue, 7);

  return {
    maintainAspectRatio: false,
    aspectRatio: 0.8,
    plugins: {
      // Интерактивные подсказки при наведении
      tooltip: {
        mode: 'index', // Показывает все значения в столбце (все категории за месяц)
        intersect: false
      },
      legend: {
        labels: {
          color: textColor,
          // Можно добавить padding или уменьшить шрифт, если категорий много
          // boxWidth: 15,
          // font: { size: 10 }
        }
      }
    },
    scales: {
      x: {
        stacked: true, // !!! Ключевая опция для оси X
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder,
          drawBorder: false // Убрать границу оси
        }
      },
      y: {
        stacked: true,
        min: 0,
        max: scale.axisMax,
        ticks: {
          color: textColorSecondary,
          // Форматирование валюты
          callback: function (value) {
            return value.toLocaleString('ru-RU') + ' ₽';
          },
          stepSize: scale.stepSize,
        },
        grid: {
          color: surfaceBorder,
          drawBorder: false // Убрать границу оси
        },
        beginAtZero: true
      }
    }
  };
}
</script>

<style scoped>
/* Можно добавить стили, если стандартных не хватает */
</style>