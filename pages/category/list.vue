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
        <div v-if="!loading && (!categories || categories.length === 0)">
          <NothingHere />
        </div>
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
        <Dialog
            v-model:visible="categoryDialog"
            :style="{ width: '90%', maxWidth: '450px' }"
            :header="isEditMode ? 'Редактирование категории' : 'Создание категории'"
            :modal="true"
            class="p-fluid"
            :dismissableMask="true"
            :closeOnEscape="true"
            :breakpoints="{ '960px': '75vw', '640px': '90vw' }"
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
        <ConfirmDialog
            :style="{ width: '90%', maxWidth: '450px' }"
            class="p-fluid"
            :closeOnEscape="true"
            :breakpoints="{ '960px': '75vw', '640px': '90vw' }">
          <template #message="slotProps">
            <div class="flex flex-col items-center text-center p-4">
              <i :class="slotProps.message.icon" class="text-3xl text-yellow-500 mb-3"></i>
              <p class="text-base">{{ slotProps.message.message }}</p>
            </div>
          </template>
          <template #footer="{ reject, accept }">
            <div class="flex justify-center gap-2 pt-3">
              <Button label="Нет" icon="pi pi-times" outlined size="small" @click="reject" />
              <Button label="Да" icon="pi pi-check" severity="danger" size="small" @click="accept" />
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

const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await instance.get('/categories/my')
    categories.value = response.data || []
  } catch (error: any) {
    console.error('Ошибка при загрузке категорий:', error)
  } finally {
    loading.value = false
  }
}

const onRowClick = (event: { data: CategoryModel }) => {
  selectedCategory.value = event.data
}

const openNewCategoryDialog = () => {
  category.value = { name: '', color: '4CAF50' }
  categoryDialog.value = true
  isEditMode.value = false
}

const editCategory = async (categoryData: CategoryModel) => {
  loading.value = true
  try {
    const response = await instance.get(`/categories/${categoryData.id}`)
    category.value = response.data
    categoryDialog.value = true
    isEditMode.value = true
  } catch (error) {
    console.error('Ошибка при получении данных категории:', error)
  } finally {
    loading.value = false
  }
}

const hideDialog = () => {
  categoryDialog.value = false
}

const saveCategory = async (event: any) => {
  if (!event.valid) {
    return
  }

  loading.value = true
  const formValues = event.values as CategoryModel;

  try {
    if (isEditMode.value) {
      await instance.patch(`/categories/${category.value.id}`, {
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
    fetchCategories()
  } catch (error: any) {
    console.error('Ошибка при сохранении категории:', error)
    displayErrorToast(error.response?.data?.detail || 'Не удалось сохранить категорию')
  } finally {
    loading.value = false
  }
}

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

const deleteCategory = async (categoryData: CategoryModel) => {
  try {
    loading.value = true
    await instance.delete(`/categories/${categoryData.id}`)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Категория "${categoryData.name}" удалена`,
      life: 3000
    })
    
    fetchCategories()
  } catch (error: any) {
    console.error('Ошибка при удалении категории:', error)
    displayErrorToast(error.response?.data?.detail || 'Не удалось удалить категорию')
  } finally {
    loading.value = false
  }
}

const displayErrorToast = (msg: string) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка',
    detail: msg,
    life: 3000
  })
}

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

.color-dot {
  display: inline-block;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.color-preview {
  display: inline-block;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

:deep(.p-button.p-button-sm .p-button-icon) {
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
}
</style>