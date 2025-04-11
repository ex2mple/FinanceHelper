<template>
  <Toast position="top-right" />
  <div class="p-4">
    <Card class="shadow-md animate-fadein">
      <template #title>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="pi pi-tag text-lg"></i>
            <span class="text-xl font-medium">Категории расходов</span>
          </div>
          <Button
            icon="pi pi-plus"
            label="Новая категория"
            size="small"
            @click="openNewCategoryDialog"
          />
        </div>
      </template>
      <template #content>
        <!-- Таблица категорий -->
        <DataTable 
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
        >
          <Column field="id" header="ID" style="width: 5rem" :sortable="true" />
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
            <div class="field mb-3">
              <label for="categoryName" class="font-medium mb-2 block">Название</label>
              <InputText 
                id="categoryName" 
                v-model="category.name" 
                :class="{'p-invalid': submitted && !category.name}" 
                autofocus
                placeholder="Введите название категории"
              />
              <Message severity="error" v-if="submitted && !category.name" class="mt-2">
                Название категории обязательно
              </Message>
            </div>
            
            <div class="field mb-3">
              <label for="categoryColor" class="font-medium mb-2 block">Цвет</label>
              <div class="flex items-center gap-2">
                <span class="color-preview" :style="{ backgroundColor: category.color }"></span>
                <ColorPicker 
                  id="categoryColor" 
                  v-model="category.color" 
                  format="hex"
                />
              </div>
              <Message severity="error" v-if="submitted && !category.color" class="mt-2">
                Выберите цвет категории
              </Message>
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end gap-2">
              <Button 
                label="Отмена" 
                icon="pi pi-times" 
                text
                @click="hideDialog" 
              />
              <Button 
                label="Сохранить" 
                icon="pi pi-check" 
                @click="saveCategory" 
                :loading="loading"
              />
            </div>
          </template>
        </Dialog>

        <!-- Диалог подтверждения удаления -->
        <ConfirmDialog></ConfirmDialog>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from '#imports'
import { useConfirm } from 'primevue/useconfirm'

// Схема категории
interface Category {
  id: number
  name: string
  color: string
}

// Изначальные категории (такие же, как в форме добавления транзакций)
const categories = ref<Category[]>([
  { id: 1, name: 'Продукты', color: '#4CAF50' },
  { id: 2, name: 'Транспорт', color: '#2196F3' },
  { id: 3, name: 'Развлечения', color: '#9C27B0' },
  { id: 4, name: 'Здоровье', color: '#F44336' },
  { id: 5, name: 'Образование', color: '#FF9800' },
  { id: 6, name: 'Кафе и рестораны', color: '#795548' },
  { id: 7, name: 'Коммунальные платежи', color: '#607D8B' },
  { id: 8, name: 'Одежда', color: '#E91E63' },
  { id: 9, name: 'Прочее', color: '#9E9E9E' }
])

const toast = useToast()
const confirm = useConfirm()
const categoryDialog = ref(false)
const submitted = ref(false)
const loading = ref(false)
const selectedCategory = ref(null)
const isEditMode = ref(false)

// Пустая категория для создания новой
const emptyCategoryTemplate = {
  id: null,
  name: '',
  color: '#4CAF50' // Цвет по умолчанию
}

const category = ref({...emptyCategoryTemplate})

// Обработчик клика по строке таблицы
const onRowClick = (event) => {
  selectedCategory.value = event.data
}

// Открыть диалог создания новой категории
const openNewCategoryDialog = () => {
  category.value = {...emptyCategoryTemplate}
  submitted.value = false
  categoryDialog.value = true
  isEditMode.value = false
}

// Открыть диалог редактирования категории
const editCategory = (categoryData) => {
  category.value = {...categoryData}
  categoryDialog.value = true
  isEditMode.value = true
}

// Скрыть диалог
const hideDialog = () => {
  categoryDialog.value = false
  submitted.value = false
}

// Сохранить категорию (добавление или редактирование)
const saveCategory = async () => {
  submitted.value = true
  
  if (!category.value.name || !category.value.color) {
    return
  }
  
  loading.value = true
  
  try {
    // Симуляция API-запроса
    await new Promise(resolve => setTimeout(resolve, 500))
    
    if (isEditMode.value) {
      // Редактирование существующей категории
      const index = categories.value.findIndex(c => c.id === category.value.id)
      if (index !== -1) {
        categories.value[index] = {...category.value}
        
        toast.add({
          severity: 'success', 
          summary: 'Успешно', 
          detail: `Категория "${category.value.name}" обновлена`,
          life: 3000
        })
      }
    } else {
      // Добавление новой категории
      const newId = Math.max(0, ...categories.value.map(c => c.id)) + 1
      const newCategory = {
        id: newId,
        name: category.value.name,
        color: category.value.color
      }
      
      categories.value.push(newCategory)
      
      toast.add({
        severity: 'success', 
        summary: 'Успешно', 
        detail: `Категория "${category.value.name}" добавлена`,
        life: 3000
      })
    }
    
    hideDialog()
  } catch (error) {
    console.error('Ошибка при сохранении категории:', error)
    toast.add({
      severity: 'error', 
      summary: 'Ошибка', 
      detail: 'Не удалось сохранить категорию',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

// Подтверждение удаления категории
const confirmDelete = (categoryData) => {
  confirm.require({
    message: `Вы уверены, что хотите удалить категорию "${categoryData.name}"?`,
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deleteCategory(categoryData),
    reject: () => {}
  })
}

// Удаление категории
const deleteCategory = async (categoryData) => {
  try {
    loading.value = true
    
    // Симуляция API-запроса
    await new Promise(resolve => setTimeout(resolve, 500))
    
    categories.value = categories.value.filter(c => c.id !== categoryData.id)
    
    toast.add({
      severity: 'success', 
      summary: 'Успешно', 
      detail: `Категория "${categoryData.name}" удалена`,
      life: 3000
    })
  } catch (error) {
    console.error('Ошибка при удалении категории:', error)
    toast.add({
      severity: 'error', 
      summary: 'Ошибка', 
      detail: 'Не удалось удалить категорию',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}
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