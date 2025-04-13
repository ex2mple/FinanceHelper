<template>
  <div class="card">
    <Chart type="line" :data="chartData" :options="chartOptions" class="h-[20rem]"/>
  </div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import Chart from 'primevue/chart';
import instance from "~/axiosinstance.js";

const chartData = ref();
const chartOptions = ref();
const transactionsData = ref()

onMounted(async () => {
  const transactions = (await instance.get('/transactions/my')).data
  const user = transactions[0].user
  transactionsData.value = {transactions: transactions, user: user}

  chartData.value = setChartData();
  chartOptions.value = setChartOptions();
})

const getAllExpenses = () => {
  const monthlyExpenses = Array(12).fill(0);

  if (!transactionsData.value || transactionsData.value.length === 0) {
    return monthlyExpenses;
  }

  transactionsData.value.transactions.forEach(transaction => {
    if (transaction.amount < 0) {
      const transactionDate = new Date(transaction.datetime);
      const monthIndex = transactionDate.getMonth();

      if (monthIndex >= 0 && monthIndex < 12) {
        monthlyExpenses[monthIndex] += Math.abs(transaction.amount);
      }
    }
  });

  return monthlyExpenses;
};

const getAllIncomes = () => {
  const monthlyIncomes = Array(12).fill(transactionsData.value.user.salary);

  if (!transactionsData.value || transactionsData.value.length === 0) {
    return monthlyIncomes;
  }

  transactionsData.value.transactions.forEach(transaction => {
    if (transaction.amount > 0) {
      const transactionDate = new Date(transaction.datetime);
      const monthIndex = transactionDate.getMonth();

      if (monthIndex >= 0 && monthIndex < 12) {
        monthlyIncomes[monthIndex] += transaction.amount;
      }
    }
  });

  return monthlyIncomes;
};

const setChartData = () => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    datasets: [
      {
        label: 'Расходы',
        data: getAllExpenses(),
        fill: false,
        borderColor: documentStyle.getPropertyValue('--p-cyan-500'),
        tension: 0.4
      },
      {
        label: 'Доходы',
        data: getAllIncomes(),
        fill: false,
        borderColor: documentStyle.getPropertyValue('--p-gray-500'),
        tension: 0.4
      }
    ]
  };
};
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
    aspectRatio: 0.6,
    plugins: {
      legend: {
        labels: {
          color: textColor
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder
        }
      },
      y: {
        min: 0,
        max: scale.axisMax,
        ticks: {
          color: textColorSecondary,
          callback: function (value) {
            return value.toLocaleString('ru-RU') + ' ₽';
          },
          stepSize: scale.stepSize,
        },
        grid: {
          color: surfaceBorder
        },
        beginAtZero: true
      }
    }
  };
}
</script>
<style scoped>

</style>