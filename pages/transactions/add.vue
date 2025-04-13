<template>
  <Toast position="top-right"/>
  <div class="flex justify-center items-center p-4 relative">
    <Card class="w-full max-w-[450px] shadow-lg border-0 animate-fadein">
      <template #title>
        <div class="flex items-center justify-between mb-3">
          <span class="text-xl font-semibold">Добавить операцию</span>
          <Button
              icon="pi pi-times"
              class="p-button-rounded p-button-text"
              severity="warn"
              @click="$router.push('/')"
              aria-label="Закрыть"
          />
        </div>
      </template>
      <template #content>
        <Form
            @submit="onSubmit"
            v-slot="form"
            :resolver="resolver"
            :initialValues="formModel"
            :validateOnValueUpdate="false"
            :validateOnBlur="false"
            :validateOnSubmit="true"
            :validateOnMount="false"
            class="p-fluid"
            ref="formRef"
        >
          <div class="grid">
            <!-- Название -->
            <div class="col-12 field mb-3">
              <label for="title" class="font-medium mb-1 block">Название</label>
              <InputText
                  id="title"
                  name="title"
                  v-model="formModel.title"
                  class="w-full"
                  :class="{'p-invalid': form.title?.invalid}"
              />
              <small v-if="form.title?.invalid" class="p-error block mt-2">
                {{ form.title.error.message }}
              </small>
            </div>

            <!-- Сумма -->
            <div class="col-12 field mb-3">
              <label for="amount" class="font-medium mb-1 block">Сумма (₽)</label>
              <InputNumber
                  id="amount"
                  name="amount"
                  v-model="formModel.amount"
                  mode="currency"
                  currency="RUB"
                  locale="ru-RU"
                  :minFractionDigits="0"
                  :maxFractionDigits="0"
                  class="w-full"
                  :class="{'p-invalid': form.amount?.invalid}"
              />
              <small v-if="form.amount?.invalid" class="p-error block mt-2">
                {{ form.amount.error.message }}
              </small>
            </div>

            <!-- Категория -->
            <div class="col-12 field mb-3">
              <label for="category" class="font-medium mb-1 block">Категория</label>
              <Dropdown
                  id="category"
                  name="category"
                  v-model="formModel.category"
                  :options="categories"
                  optionLabel="name"
                  class="w-full"
                  :class="{'p-invalid': form.category?.invalid}"
                  placeholder="Выберите категорию"
                  filter
                  filterPlaceholder="Поиск категории"
              >
                <template #value="slotProps">
                  <div v-if="slotProps.value" class="flex align-items-center">
                    <span class="w-2 h-2 mr-2 rounded-full"
                          :style="`background-color: ${slotProps.value.color}`"></span>
                    <div>{{ slotProps.value.name }}</div>
                  </div>
                  <span v-else>Выберите категорию</span>
                </template>
                <template #option="slotProps">
                  <div class="flex align-items-center">
                    <span class="w-2 h-2 mr-2 rounded-full"
                          :style="`background-color: ${slotProps.option.color}`"></span>
                    <div>{{ slotProps.option.name }}</div>
                  </div>
                </template>
              </Dropdown>
              <small v-if="form.category?.invalid" class="p-error block mt-2">
                {{ form.category.error.message }}
              </small>
            </div>

            <!-- Дата и время -->
            <div class="col-12 field mb-3">
              <label for="datetime" class="font-medium mb-1 block">Дата и время</label>
              <Calendar
                  id="datetime"
                  name="datetime"
                  v-model="formModel.datetime"
                  showTime
                  hourFormat="24"
                  :showIcon="true"
                  class="w-full"
                  :class="{'p-invalid': form.datetime?.invalid}"
                  :maxDate="maxDate"
                  placeholder="Выберите дату и время"
              />
              <small v-if="form.datetime?.invalid" class="p-error block mt-2">
                {{ form.datetime.error.message }}
              </small>
            </div>

            <div>
            <label for="type" class="block text-gray-700 mb-1">Тип операции</label>
            <div class="flex justify-content-center">
              <SelectButton
                  id="type"
                  name="type"
                  v-model="formModel.type"
                  :options="[
                  { label: 'Расход', value: 'expense' },
                  { label: 'Доход', value: 'income' },
                ]"
                  optionLabel="label"
                  optionValue="value"
                  :class="{'p-invalid': form.type?.invalid}"
              />
            </div>
            <small v-if="form.type?.invalid" class="p-error block mt-2">
              {{ form.type.error.message }}
            </small>
          </div>

            <!-- Кнопки -->
            <div class="col-12 mt-3 grid grid-cols-1 gap-2">
              <!-- Кнопка сканирования чека -->
              <Button
                  type="button"
                  icon="pi pi-camera"
                  label="Сканировать чек"
                  severity="secondary"
                  outlined
                  class="w-full mb-2"
                  @click="$router.push('/scan')"
              />

              <!-- Кнопка сохранения -->
              <Button
                  type="submit"
                  icon="pi pi-check"
                  label="Сохранить"
                  class="w-full"
                  :loading="loading"
              />
            </div>
          </div>
        </Form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import * as yup from 'yup'
import { yupResolver } from '@primevue/forms/resolvers/yup'
import { useToast, useRoute } from '#imports'
import { requiredError } from '~/constants/defaultErrorMessages'
import instance from "~/axiosInstance";
import { ref, reactive, onMounted } from 'vue'

// Define interfaces for better type safety
interface Category {
  id: number;
  name: string;
  color: string;
  [key: string]: any;
}

interface TransactionFormData {
  title: string;
  amount: number | null;
  category: Category | null;
  datetime: Date;
  type: 'expense' | 'income';
}

// Yup schema for form validation
const transactionSchema = yup.object({
  title: yup.string().required(requiredError).max(100, 'Максимальная длина 100 символов'),
  amount: yup.number().required(requiredError).min(0, 'Сумма должна быть больше 0').max(100000000, 'Слишком много'),
  category: yup.object().required(requiredError),
  datetime: yup.date().required(requiredError).max(new Date(), 'Дата не может быть в будущем'),
})

const resolver = yupResolver(transactionSchema)

const toast = useToast()
const route = useRoute()
const router = useRouter()

const maxDate = ref(new Date())
const loading = ref(false)
const categories = ref<Category[]>([])
const formRef = ref(null)

// Flag to track if form was pre-filled from QR code
const prefilled = ref(false)

// Create reactive form model with proper types
const formModel = reactive<TransactionFormData>({
  title: '',
  amount: null,
  category: null,
  datetime: new Date(),
  type: 'expense'
})

// Проверяем, есть ли данные в query-параметрах (из сканирования чека)
onMounted(async () => {
  try {
    // Получаем список категорий
    const response = await instance.get('/categories/my')
    categories.value = response.data
    
    // Проверяем, пришли ли данные со страницы сканирования
    if (route.query.title) {
      prefilled.value = true
      
      // Находим категорию по id из параметров
      if (route.query.category_id && categories.value.length > 0) {
        const categoryId = parseInt(route.query.category_id as string)
        const selectedCategory = categories.value.find(cat => cat.id === categoryId)
        if (selectedCategory) {
          formModel.category = selectedCategory
        }
      }
      
      // Заполняем значения формы из query-параметров напрямую в реактивную модель
      formModel.title = route.query.title as string
      formModel.amount = route.query.amount ? parseFloat(route.query.amount as string) : null
      formModel.datetime = route.query.datetime ? new Date(route.query.datetime as string) : new Date()
      formModel.type = (route.query.type as 'expense' | 'income') || 'expense'
    }
  } catch(error) {
    console.error('Ошибка при загрузке данных:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить данные категорий',
      life: 3000
    })
  }
})

// Submit handler with improved type safety and validation
const onSubmit = async (data: { values: any; valid: boolean }) => {
  // For pre-filled forms, bypass validation if data is valid
  if (prefilled.value) {
    // Manual validation for pre-filled forms
    const isValid = Boolean(
      formModel.title && 
      formModel.amount !== null && 
      formModel.amount > 0 && 
      formModel.category &&
      formModel.datetime
    )
    
    if (isValid) {
      await submitTransaction()
      return
    }
  }
  
  // Normal validation flow for user-filled forms
  if (!data.valid) {
    // Не выводим уведомление об ошибке валидации
    return
  }
  
  await submitTransaction()
}

// Extracted submission logic with improved error handling
const submitTransaction = async () => {
  if (!formModel.category) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Выберите категорию',
      life: 3000
    })
    return
  }

  // Create transaction data object with rounded amount
  const roundedAmount = formModel.amount ? Math.round(Number(formModel.amount)) : 0
  
  const newData = {
    title: formModel.title,
    amount: formModel.type === "expense" ? -Math.abs(roundedAmount) : Math.abs(roundedAmount),
    category_id: formModel.category.id,
    datetime: formModel.datetime,
    type: formModel.type
  }
  
  loading.value = true

  try {
    await instance.post('/transactions/create', newData)

    toast.add({
      severity: 'success',
      summary: 'Готово',
      detail: 'Транзакция успешно добавлена',
      life: 3000,
    })
    navigateTo('/')
  } catch (error: any) {
    console.error('Ошибка при сохранении:', error)

    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: error.message || 'Не удалось сохранить транзакцию',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.p-card {
  border-radius: 10px;
}

.animate-fadein {
  animation: fadeIn 0.3s ease-out;
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

:deep(.p-card-content) {
  padding-top: 0 !important;
}

:deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item) {
  padding: 0.5rem 1rem;
}

/* Уменьшаем размеры компонентов */
:deep(.p-inputtext),
:deep(.p-dropdown),
:deep(.p-calendar),
:deep(.p-inputnumber),
:deep(.p-textarea) {
  font-size: 0.95rem;
}

:deep(.p-button) {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
}

:deep(.p-button .p-button-icon) {
  font-size: 0.9rem;
}

/* Удаление предыдущих стилей для кнопки QR-кода */
.qr-scan-button {
  display: none;
}
</style>