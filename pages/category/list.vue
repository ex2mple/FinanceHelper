<template>
  <Toast position="top-right"/>
  <div class="p-4">
    <Card class="shadow-md animate-fadein">
      <template #title>
        <div class="flex items-center justify-between pl-2 p-4">
          <div class="flex items-center gap-2">
            <span class="text-xl font-medium">Категории расходов</span>
          </div>
          <Button
            icon="pi pi-plus"
            size="small"
            class="rounded-full w-8 h-8"
            @click="openNewCategoryDialog"
        />
        </div>
      </template>
      <template #content>
        <!-- Компонент NothingHere, если нет данных -->
        <div v-if="!loading && (!categories || categories.length === 0)">
          <NothingHere />
        </div>
        
        <!-- Таблица категорий, если есть данные -->
        <DataTable
            v-else
            :value="categories"
            stripedRows
            :paginator="categories.length > 10"
            :rows="10"
            dataKey="id"
            v-model:selection="selectedCategory"
            selectionMode="single"
            @row-click="onRowClick"
            class="p-datatable-sm"
            :rowHover="true"
            responsiveLayout="scroll"
            emptyMessage="Нет доступных категорий"
            currentPageReportTemplate="{first} - {last} из {totalRecords}"
            :pageLinkSize="3"
            :loading="loading"
        >
          <Column field="name" header="Название" :sortable="true">
            <template #body="slotProps">
              <div class="flex items-center gap-2">
                <span class="color-dot" :style="{ backgroundColor: slotProps.data.color }"></span>
                <span>{{ slotProps.data.name }}</span>
              </div>
            </template>
          </Column>
          <Column header="Действия" style="width: 8rem">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button
                    icon="pi pi-pencil"
                    @click.stop="editCategory(slotProps.data)"
                    text
                    size="small"
                    aria-label="Редактировать"
                />
                <Button
                    icon="pi pi-trash"
                    @click.stop="confirmDelete(slotProps.data)"
                    text
                    severity="danger"
                    size="small"
                    aria-label="Удалить"
                />
              </div>
            </template>
          </Column>
        </DataTable>

        <!-- Модальное окно добавления/редактирования категории -->
        <Dialog
            v-model:visible="categoryDialog"
            :style="{ width: '450px' }"
            :header="isEditMode ? 'Редактирование категории' : 'Создание категории'"
            :modal="true"
            class="p-fluid"
            :dismissableMask="true"
            :closeOnEscape="true"
        >
          <div class="p-fluid">
            <Form 
              @submit="saveCategory" 
              v-slot="form" 
              :resolver="resolver"
              :validateOnValueUpdate="false"
              :validateOnBlur="true" 
              :initial-values="category"
            >
              <div class="field mb-3">
                <label for="categoryName" class="font-medium mb-2 block">Название</label>
                <InputText
                    id="categoryName"
                    name="name"
                    :class="{'p-invalid': form.name?.invalid}"
                    autofocus
                    placeholder="Введите название категории"
                />
                <Message severity="error" v-if="form.name?.invalid" class="mt-2">
                  {{ form.name.error.message }}
                </Message>
              </div>

              <div class="field mb-3">
                <label for="categoryColor" class="font-medium mb-2 block">Цвет</label>
                <div class="flex items-center gap-2">
                  <ColorPicker
                      id="categoryColor"
                      name="color"
                      format="hex"
                  />
                </div>
                <Message severity="error" v-if="form.color?.invalid" class="mt-2">
                  {{ form.color.error.message }}
                </Message>
              </div>
              
              <div class="flex justify-end gap-2 mt-4">
                <Button
                    type="button"
                    label="Отмена"
                    icon="pi pi-times"
                    text
                    @click="hideDialog"
                />
                <Button
                    type="submit"
                    label="Сохранить"
                    icon="pi pi-check"
                    :loading="!!form.isSubmitting"
                />
              </div>
            </Form>
          </div>
        </Dialog>

        <!-- Диалог подтверждения удаления -->
        <ConfirmDialog>
          <template #message="slotProps">
                <div class="flex flex-col items-center w-full gap-4 border-b border-surface-200 dark:border-surface-700">
                  <i :class="slotProps.message.icon" class="text-5xl text-primary-500"></i>
                  <p class="pb-4">{{ slotProps.message.message }}</p>
                </div>
          </template>
        </ConfirmDialog>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '#imports'
import { useConfirm } from 'primevue/useconfirm'
import { yupResolver } from '@primevue/forms/resolvers/yup'
import { categorySchema, type CategoryModel } from '~/types/categoryModel'
import instance from '~/axiosInstance'
import NothingHere from '~/components/NothingHere.vue'
import { onMounted, ref } from 'vue' // Added explicit imports

const toast = useToast()
const confirm = useConfirm()
const categoryDialog = ref(false)
const loading = ref(false)
const selectedCategory = ref<CategoryModel | null>(null)
const isEditMode = ref(false)
const categories = ref<CategoryModel[]>([])
const category = ref<CategoryModel>({ 
  name: '', 
  color: '4CAF50'
})
const resolver = yupResolver(categorySchema)

// Получение категорий с сервера
const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await instance.get('/categories/my')
    categories.value = response.data || []
  } catch (error: any) {
    console.error('Ошибка при загрузке категорий:', error)
    displayErrorToast('Не удалось загрузить категории')
  } finally {
    loading.value = false
  }
}

// Обработчик клика по строке таблицы
const onRowClick = (event: { data: CategoryModel }) => {
  selectedCategory.value = event.data
}

// Открыть диалог создания новой категории
const openNewCategoryDialog = () => {
  category.value = { name: '', color: '4CAF50' }
  categoryDialog.value = true
  isEditMode.value = false
}

// Открыть диалог редактирования категории
const editCategory = async (categoryData: CategoryModel) => {
  loading.value = true
  try {
    // Используем новый эндпоинт /api/v1/categories/{category_id}
    const response = await instance.get(`/categories/${categoryData.id}`)
    category.value = response.data
    categoryDialog.value = true
    isEditMode.value = true
  } catch (error) {
    console.error('Ошибка при получении данных категории:', error)
    displayErrorToast('Не удалось загрузить данные категории')
  } finally {
    loading.value = false
  }
}

// Скрыть диалог
const hideDialog = () => {
  categoryDialog.value = false
}

// Сохранить категорию (добавление или редактирование)
const saveCategory = async (event: any) => {
  if (!event.valid) {
    return
  }

  loading.value = true
  const formValues = event.values as CategoryModel;

  try {
    if (isEditMode.value) {
      // Редактирование существующей категории
      await instance.patch(`/categories/${formValues.id}`, {
        name: formValues.name,
        color: "#"+formValues.color
      })

      toast.add({
        severity: 'success',
        summary: 'Успешно',
        detail: `Категория "${formValues.name}" обновлена`,
        life: 3000
      })
    } else {
      // Добавление новой категории - используем эндпоинт без user_id
      await instance.post('/categories/create', {
        name: formValues.name,
        color: "#"+formValues.color
      })

      toast.add({
        severity: 'success',
        summary: 'Успешно',
        detail: `Категория "${formValues.name}" добавлена`,
        life: 3000
      })
    }

    hideDialog()
    fetchCategories() // Обновляем список категорий
  } catch (error: any) {
    console.error('Ошибка при сохранении категории:', error)
    displayErrorToast(error.response?.data?.detail || 'Не удалось сохранить категорию')
  } finally {
    loading.value = false
  }
}

// Подтверждение удаления категории
const confirmDelete = (categoryData: CategoryModel) => {
  confirm.require({
    message: `Вы уверены, что хотите удалить категорию "${categoryData.name}"?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Нет',
      icon: 'pi pi-times',
      outlined: true,
      size: 'small'
    },
    acceptProps: {
      label: 'Да',
      icon: 'pi pi-check',
      size: 'small'
    },
    acceptClass: 'p-button-danger',
    accept: () => deleteCategory(categoryData),
    reject: () => {}
  })
}

// Удаление категории
const deleteCategory = async (categoryData: CategoryModel) => {
  try {
    loading.value = true
    // Используем новый эндпоинт для удаления: /api/v1/categories/{category_id}
    await instance.delete(`/categories/${categoryData.id}`)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Категория "${categoryData.name}" удалена`,
      life: 3000
    })
    
    fetchCategories() // Обновляем список категорий
  } catch (error: any) {
    console.error('Ошибка при удалении категории:', error)
    displayErrorToast(error.response?.data?.detail || 'Не удалось удалить категорию')
  } finally {
    loading.value = false
  }
}

// Отображение ошибки
const displayErrorToast = (msg: string) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка',
    detail: msg,
    life: 3000
  })
}

// Call fetchCategories when component mounts
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
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

/* Компактные цветовые индикаторы */
.color-dot {
  display: inline-block;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Предпросмотр цвета в модальном окне */
.color-preview {
  display: inline-block;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Более компактные и стильные кнопки */
:deep(.p-button.p-button-sm .p-button-icon) {
  font-size: 0.875rem;
}

/* DataTable стили */
:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
}
</style>