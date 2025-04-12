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
            :validateOnValueUpdate="false"
            :validateOnBlur="true"
            class="p-fluid"
        >
          <div class="grid">
            <!-- Название -->
            <div class="col-12 field mb-3">
              <label for="title" class="font-medium mb-1 block">Название</label>
              <InputText
                  id="title"
                  name="title"
                  class="w-full"
                  :class="{'p-invalid': form.title?.invalid}"
              />
              <Message v-if="form.title?.invalid" severity="error" class="mt-2">
                {{ form.title.error.message }}
              </Message>
            </div>

            <!-- Сумма -->
            <div class="col-12 field mb-3">
              <label for="amount" class="font-medium mb-1 block">Сумма (₽)</label>
              <InputNumber
                  id="amount"
                  name="amount"
                  mode="currency"
                  currency="RUB"
                  locale="ru-RU"
                  class="w-full"
                  :class="{'p-invalid': form.amount?.invalid}"
              />
              <Message v-if="form.amount?.invalid" severity="error" class="mt-2">
                {{ form.amount.error.message }}
              </Message>
            </div>

            <!-- Категория -->
            <div class="col-12 field mb-3">
              <label for="category" class="font-medium mb-1 block">Категория</label>
              <Dropdown
                  id="category"
                  name="category"
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
              <Message v-if="form.category?.invalid" severity="error" class="mt-2">
                {{ form.category.error.message }}
              </Message>
            </div>

            <!-- Дата и время -->
            <div class="col-12 field mb-3">
              <label for="datetime" class="font-medium mb-1 block">Дата и время</label>
              <Calendar
                  id="datetime"
                  name="datetime"
                  showTime
                  hourFormat="24"
                  :showIcon="true"
                  class="w-full"
                  :class="{'p-invalid': form.datetime?.invalid}"
                  :maxDate="maxDate"
                  placeholder="Выберите дату и время"
              />
              <Message v-if="form.datetime?.invalid" severity="error" class="mt-2">
                {{ form.datetime.error.message }}
              </Message>
            </div>

            <div>
            <label for="type" class="block text-white mb-1">Тип операции</label>
            <div class="flex justify-content-center">
              <SelectButton
                  id="type"
                  name="type"
                  :options="[
                  { label: 'Расход', value: 'expense' },
                  { label: 'Доход', value: 'income' },
                ]"
                  optionLabel="label"
                  optionValue="value"
                  :class="{'p-invalid': form.type?.invalid}"
              />
            </div>
            <Message v-if="form.type?.invalid" severity="error" class="mt-2">
              {{ form.type.error.message }}
            </Message>
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
import {yupResolver} from '@primevue/forms/resolvers/yup'
import {useToast} from '#imports'
import {requiredError} from '~/constants/defaultErrorMessages'
import instance from "~/axiosinstance";

const transactionSchema = yup.object({
  title: yup.string().required(requiredError).max(100, 'Максимальная длина 55 символов'),
  amount: yup.number().required(requiredError).min(0, 'Сумма должна быть больше 0').max(100000000, 'Слишком много'),
  category: yup.object().required(requiredError),
  datetime: yup.date().required(requiredError).max(new Date(), 'Дата не может быть в будущем'),
})


const resolver = yupResolver(transactionSchema)

const toast = useToast()

const maxDate = ref(new Date())

const loading = ref(false)

const categories = ref()

onMounted(async () => {
  try {
    categories.value = (await instance.get('/categories/my')).data
  } catch(error) {
    console.log(error)
  }
})

const onSubmit = async (data: any) => {
  if (!data.valid) {
    return
  }

  const newData = {...data.values, category_id: data.values.category.id}
  delete newData['category']

  if (data.values.type === "expense") {
    newData.amount = -newData.amount
  }

  loading.value = true

  try {
    console.log(newData)
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