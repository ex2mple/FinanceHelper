<template>
  <div class="p-4 md:p-6">
    <Toast position="top-right"/>
    <ConfirmDialog/>

    <!-- Заголовок -->
    <h1 class="text-2xl font-semibold mb-6">Профиль пользователя</h1>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="flex justify-center items-center py-10">
      <ProgressSpinner strokeWidth="4" animationDuration=".5s" style="width: 50px; height: 50px"/>
    </div>

    <!-- Сообщение об ошибке -->
    <div v-else-if="error" class="text-center py-10">
      <Message severity="error" :closable="false">{{ error }}</Message>
      <Button label="Попробовать снова" icon="pi pi-refresh" class="p-button-text mt-4" @click="fetchData"/>
    </div>

    <!-- Основной контент -->
    <div v-else-if="userData" class="grid grid-cols-1 md:grid-cols-3 gap-6">

      <!-- Карта Профиля (слева) -->
      <Card class="md:col-span-2 shadow-md border-0">
        <template #title>
          <div class="flex items-center justify-between gap-4">
            <span>Информация</span>
            <div>
              <Button
                  :icon="isEditing ? 'pi pi-times' : 'pi pi-user-edit'"
                  :label="isEditing ? 'Отмена' : 'Редактировать'"
                  :severity="isEditing ? 'secondary' : 'primary'"
                  class="p-button-text p-button-sm"
                  @click="toggleEditMode"
              />
<!--              <Button-->
<!--                  v-if="!isEditing"-->
<!--                  icon="pi pi-trash"-->
<!--                  label="Удалить уч. запись"-->
<!--                  severity="danger"-->
<!--                  class="p-button-text p-button-sm"-->
<!--                  @click="confirmDeleteAccount"-->
<!--                  :loading="isDeleting"-->
<!--              />-->
            </div>
          </div>
        </template>
        <template #content>
          <!-- Режим отображения -->
          <div v-if="!isEditing" class="space-y-4">
            <div class="flex items-center">
              <Avatar icon="pi pi-user" size="xlarge" shape="circle" class="mr-4 bg-primary text-primary-contrast"/>
              <div>
                <div class="text-xl font-semibold">{{ userData.username }}</div>
                <div class="text-sm text-color-secondary">{{ userData.email }}</div>
              </div>
            </div>
            <Divider/>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-color-secondary mb-1">Пол</div>
                <Tag :value="userData.gender === 'Male' ? 'Мужской' : 'Женский'"
                     :severity="userData.gender === 'Male' ? 'info' : 'danger'"></Tag>
              </div>
              <div>
                <div class="text-xs text-color-secondary mb-1">Возраст</div>
                <div class="font-medium">{{ userData.age }} {{ getAgeSuffix(userData.age) }}</div>
              </div>
              <div>
                <div class="text-xs text-color-secondary mb-1">Зарплата</div>
                <div class="font-medium">{{ formatCurrency(userData.salary) }}</div>
              </div>
            </div>
          </div>

          <!-- Режим редактирования -->
          <Form
              @submit="saveProfile"
              v-slot="form"
              :resolver="resolver"
              :validateOnValueUpdate="false"
              :validateOnBlur="true"
              :initial-values="userData"
              class="space-y-4"
              v-else
          >
            <div>
            <span class="flex flex-col gap-1">
              <label for="email">Email</label>
              <InputText
                  id="email"
                  type="text"
                  name="email"
                  class="w-full rounded-lg p-input-filled"
                  :class="{'p-invalid': form.email?.invalid}"
              />
            </span>
              <Message v-if="form.email?.invalid" severity="error" class="mt-2">
                {{ form.email.error.message }}
              </Message>
            </div>

            <div>
            <span class="flex flex-col gap-1">
              <label for="first_name">Ваше имя</label>
              <InputText
                  id="username"
                  type="text"
                  name="username"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.username?.invalid}"
              />
            </span>
              <Message v-if="form.username?.invalid" severity="error" class="mt-2">
                {{ form.username.error.message }}
              </Message>
            </div>

            <div>
            <span class="flex flex-col gap-1">
              <label for="password">Пароль</label>
              <Password
                  id="password"
                  name="password"
                  toggleMask
                  :feedback="true"
                  class="w-full"
                  inputClass="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.password?.invalid}"
                  :weakLabel="'Слабый'"
                  :mediumLabel="'Средний'"
                  :strongLabel="'Сильный'"
                  :inputStyle="{ width: '100%' }"
              />
            </span>
              <Message v-if="form.password?.invalid" severity="error" class="mt-2">
                {{ form.password.error.message }}
              </Message>
            </div>

            <div>
              <label for="gender" class="block text-white mb-1">Пол</label>
              <div class="flex justify-content-center">
                <SelectButton
                    id="gender"
                    name="gender"
                    :options="[
                  { label: 'Мужской', value: 'Male' },
                  { label: 'Женский', value: 'Female' },
                ]"
                    optionLabel="label"
                    optionValue="value"
                    :class="{'p-invalid': form.gender?.invalid}"
                />
              </div>
              <Message v-if="form.gender?.invalid" severity="error" class="mt-2">
                {{ form.gender.error.message }}
              </Message>
            </div>

            <div>
            <span class="flex flex-col gap-1">
              <label for="age">Возраст</label>
              <InputNumber
                  id="age"
                  name="age"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.age?.invalid}"
                  :min="0"
              />
            </span>
              <Message v-if="form.age?.invalid" severity="error" class="mt-2">
                {{ form.age.error.message }}
              </Message>
            </div>

            <div>
            <span class="flex flex-col gap-1">
              <label for="salary">Зарплата</label>
              <InputNumber
                  id="salary"
                  name="salary"
                  mode="currency"
                  currency="RUB"
                  locale="ru-RU"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.salary?.invalid}"
                  :min="0"
              />
            </span>
              <Message v-if="form.salary?.invalid" severity="error" class="mt-2">
                {{ form.salary.error.message }}
              </Message>
            </div>

            <div class="pt-4">
              <Button
                  type="submit"
                  label="Сохранить"
                  class="w-full"
                  :loading="!!form.isSubmitting"
              />
            </div>
          </Form>
        </template>
      </Card>

      <!-- Карта Сводки (справа) -->
      <Card class="shadow-md border-0">
        <template #title>Общая сводка</template>
        <template #content>
          <div v-if="isSummaryLoading" class="flex justify-center items-center py-5">
            <ProgressSpinner strokeWidth="5" style="width: 30px; height: 30px"/>
          </div>
          <div v-else-if="summaryError" class="text-center py-5">
            <small class="text-red-500">{{ summaryError }}</small>
          </div>
          <div v-else class="space-y-4">
            <Divider class="h-1"/> <!-- Тонкий разделитель -->
            <div>
              <div class="text-xs text-color-secondary mb-1">Общие расходы</div>
              <div class="text-lg font-semibold text-red-600">{{ formatCurrency(totalExpenses) }}</div>
            </div>
            <Divider class="h-1"/>
            <div>
              <div class="text-xs text-color-secondary mb-1">Средние траты в день</div>
              <div class="text-lg font-semibold text-orange-600">{{ formatCurrency(averageDailyExpense) }}</div>
            </div>
            <Divider class="h-1"/>
            <div>
              <div class="text-xs text-color-secondary mb-1">Рекордный расход</div>
              <div v-if="recordExpenseTransaction">
                <div class="text-lg font-semibold text-red-600">
                  {{ formatCurrency(Math.abs(recordExpenseTransaction.amount)) }}
                </div>
                <div class="text-xs text-color-secondary mt-1 truncate" :title="recordExpenseTransaction.title">
                  {{ recordExpenseTransaction.title }} ({{ formatDateShort(recordExpenseTransaction.datetime) }})
                </div>
              </div>
              <div v-else class="text-sm text-color-secondary italic">
                Нет данных о расходах
              </div>
            </div>
          </div>
        </template>
      </Card>

    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, computed, reactive} from 'vue';
import {useToast} from 'primevue/usetoast';
import instance from '~/axiosinstance'; // Ваш axios инстанс

// PrimeVue компоненты
import Card from 'primevue/card';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Tag from 'primevue/tag';
import Divider from 'primevue/divider';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Password from 'primevue/password';
import Toast from 'primevue/toast';
import {type EditUser, editUserSchema} from "~/types/authModels";
import {type TransactionModel} from "~/types/transactionModel";
import {yupResolver} from "@primevue/forms/resolvers/yup";

// --- Состояние компонента ---
const toast = useToast();
const userData = ref<EditUser | null>(null);
const transactionsData = ref<TransactionModel[]>([]); // Для сводки
const isEditing = ref(false);
const isLoading = ref(true); // Общая загрузка страницы
const isSaving = ref(false); // Загрузка при сохранении
const isSummaryLoading = ref(true); // Загрузка данных для сводки
const error = ref<string | null>(null); // Ошибка загрузки профиля
const summaryError = ref<string | null>(null); // Ошибка загрузки транзакций

const resolver = yupResolver(editUserSchema)

// Форма редактирования (используем reactive для простоты)
// Инициализируем пустыми значениями, заполним при переходе в режим редактирования
const formData = reactive<Partial<EditUser & { password?: string }>>({
  username: '',
  email: '',
  gender: 'Female',
  age: 0,
  salary: 0,
  password: '' // Добавляем поле для пароля
});


// --- API Запросы ---
const fetchUserData = async () => {
  try {
    // Замените на ваш реальный эндпоинт получения текущего пользователя
    const response = await instance.get<EditUser>('/auth/me');
    userData.value = response.data;
  } catch (err: any) {
    console.error("Ошибка загрузки профиля:", err);
    throw new Error("Не удалось загрузить данные профиля."); // Передаем ошибку дальше
  }
};

const fetchTransactions = async () => {
  try {
    const response = await instance.get<TransactionModel[]>('/transactions/my');
    transactionsData.value = response.data || [];
  } catch (err: any) {
    console.error("Ошибка загрузки транзакций:", err);
    summaryError.value = "Не удалось загрузить сводку."; // Показываем ошибку локально для сводки
  } finally {
    isSummaryLoading.value = false;
  }
};

// Функция для получения всех данных при монтировании
const fetchData = async () => {
  isLoading.value = true;
  isSummaryLoading.value = true; // Сбрасываем лоадер сводки
  error.value = null;
  summaryError.value = null;
  try {
    // Запускаем параллельно
    await Promise.all([
      fetchUserData(),
      fetchTransactions() // Загрузка транзакций для сводки
    ]);
  } catch (err: any) {
    error.value = err.message || "Произошла ошибка при загрузке данных."; // Показываем общую ошибку
  } finally {
    isLoading.value = false;
  }
};

const displayErrorToast = (msg: string) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка сохранения профиля',
    detail: msg,
    life: 2500,
  })
}

// Сохранение профиля
const saveProfile = async (data: { valid: Boolean; values: EditUser }) => {
  isSaving.value = true;
  if (!data.valid) {
    displayErrorToast('Проверьте правильность введенных данных')
    return
  }

  try {
    const response = await instance.patch('/users/update', data.values)
    userData.value = response.data;
    toggleEditMode()
  } catch (err: any) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    console.error(errorMessage)
    displayErrorToast(err.response.data?.detail)
  } finally {
    isSaving.value = false;
  }
};

// --- Логика редактирования ---
const toggleEditMode = () => {
  if (isEditing.value) {
    cancelEdit(); // Если кликнули "Отмена"
  } else {
    editProfile(); // Если кликнули "Редактировать"
  }
};

const editProfile = () => {
  if (!userData.value) return;
  // Копируем текущие данные пользователя в форму
  formData.username = userData.value.username;
  formData.email = userData.value.email;
  formData.gender = userData.value.gender;
  formData.age = userData.value.age;
  formData.salary = userData.value.salary;
  formData.password = ''; // Сбрасываем поле пароля при каждом входе в редактирование
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

// --- Вычисляемые свойства для сводки ---
const totalIncome = computed(() => {
  return transactionsData.value
      .filter(tx => tx.amount > 0)
      .reduce((sum, tx) => sum + tx.amount, 0);
});

const totalExpenses = computed(() => {
  // Возвращаем положительное число для отображения
  return Math.abs(transactionsData.value
      .filter(tx => tx.amount < 0)
      .reduce((sum, tx) => sum + tx.amount, 0));
});

const netBalance = computed(() => {
  // Вычисляем из исходных сумм (доход - абсолютные расходы)
  return transactionsData.value.reduce((sum, tx) => sum + tx.amount, 0);
});

// --- Вспомогательные функции ---
const formatCurrency = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '0 ₽';
  return value.toLocaleString('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
};

const getAgeSuffix = (age: number | null | undefined): string => {
  if (age === null || age === undefined) return '';
  const lastDigit = age % 10;
  const lastTwoDigits = age % 100;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
    return 'лет';
  }
  if (lastDigit === 1) {
    return 'год';
  }
  if (lastDigit >= 2 && lastDigit <= 4) {
    return 'года';
  }
  return 'лет';
};

const averageDailyExpense = computed(() => {
  const expenses = transactionsData.value.filter(tx => tx.amount < 0);
  if (!expenses.length) {
    return 0; // Нет расходов - нет среднего
  }

  // Находим общую сумму расходов (абсолютное значение)
  const totalAbsoluteExpenses = expenses.reduce((sum, tx) => sum + Math.abs(tx.amount), 0);

  // Находим диапазон дат ВСЕХ транзакций для расчета количества дней
  if (transactionsData.value.length === 0) {
    return 0; // Нет транзакций - нет периода
  }

  let minDate = new Date(transactionsData.value[0].datetime);
  let maxDate = new Date(transactionsData.value[0].datetime);

  transactionsData.value.forEach(tx => {
    try {
      const currentDate = new Date(tx.datetime);
      if (currentDate < minDate) minDate = currentDate;
      if (currentDate > maxDate) maxDate = currentDate;
    } catch (e) {
      console.error("Invalid date encountered:", tx.datetime);
      // Пропускаем невалидную дату
    }
  });

  // Разница в миллисекундах
  const diffTime = Math.abs(maxDate.getTime() - minDate.getTime());
  // Количество дней (+1, т.к. включаем обе даты)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

  // Чтобы избежать деления на 0, если все транзакции в один день (diffTime=0)
  const numberOfDays = Math.max(1, diffDays);

  return totalAbsoluteExpenses / numberOfDays;
});

// НОВОЕ: Нахождение транзакции с рекордным расходом
const recordExpenseTransaction = computed(() => {
  const expenses = transactionsData.value.filter(tx => tx.amount < 0);
  if (!expenses.length) {
    return null; // Нет расходов
  }

  // Находим транзакцию с минимальным значением amount (самый большой расход)
  return expenses.reduce((maxExpenseTx, currentTx) => {
    return currentTx.amount < maxExpenseTx.amount ? currentTx : maxExpenseTx;
  }, expenses[0]); // Начинаем сравнение с первой транзакции
});

// --- Вспомогательные функции (дополненные) ---

// НОВАЯ: Форматирование даты для рекорда
const formatDateShort = (dateString: string | null | undefined): string => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    // Формат: ДД.ММ.ГГГГ или ДД мес. ГГГГ
    return date.toLocaleDateString('ru-RU', {day: 'numeric', month: 'short', year: 'numeric'});
  } catch (e) {
    return 'Неверная дата';
  }
};

const confirm = useConfirm();
const router = useRouter();
const isDeleting = ref(false);

const confirmDeleteAccount = () => {
  confirm.require({
    message: 'Вы уверены, что хотите удалить свою учетную запись? Это действие необратимо.',
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Да, удалить',
    rejectLabel: 'Отмена',
    acceptIcon: 'pi pi-trash',
    rejectIcon: 'pi pi-times',
    acceptClass: 'p-button-danger', // Style the accept button as danger
    rejectClass: 'p-button-text',
    accept: async () => {
      // This function is called if the user clicks "Yes"
      await deleteAccount();
    },
    reject: () => {
      // Optional: Called if the user clicks "No" or closes the dialog
      toast.add({severity: 'info', summary: 'Отменено', detail: 'Удаление учетной записи отменено', life: 3000});
    }
  });
};

// Function to handle the actual API call and logout
const deleteAccount = async () => {
  isDeleting.value = true;
  try {
    // Replace with your actual API endpoint for user deletion
    await instance.delete('/users/');

    toast.add({severity: 'success', summary: 'Успешно', detail: 'Ваша учетная запись была удалена.', life: 5000});

    await router.push('/login');

  } catch (err: any) {
    console.error("Ошибка удаления учетной записи:", err);
    const errorDetail = err.response?.data?.detail || 'Не удалось удалить учетную запись.';
    toast.add({severity: 'error', summary: 'Ошибка', detail: errorDetail, life: 5000});
  } finally {
    isDeleting.value = false;
  }
};

// --- Загрузка данных при монтировании ---
onMounted(() => {
  fetchData();
});

</script>

<style scoped>
/* Дополнительные стили при необходимости */
.p-card .p-card-content {
  padding-top: 0.5rem; /* Уменьшить отступ сверху в карточках */
}

.p-divider-horizontal {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>