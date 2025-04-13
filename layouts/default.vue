<template>
  <header>
    <Menubar :model="items">
      <template #item="{ item, props, hasSubmenu, root }">
        <a v-ripple class="flex items-center" v-bind="props.action">
          <i v-if="item.icon" :class="['mr-2', item.icon]"></i>
          <span>{{ item.label }}</span>
          <Badge
            v-if="item.badge"
            :class="{ 'ml-auto': !root, 'ml-2': root }"
            :value="item.badge"
          />
          <span
            v-if="item.shortcut"
            class="border-surface bg-emphasis text-muted-color ml-auto rounded border p-1 text-xs"
            >{{ item.shortcut }}</span
          >
          <i
            v-if="hasSubmenu"
            :class="[
              'pi pi-angle-down ml-auto',
              { 'pi-angle-down': root, 'pi-angle-right': !root },
            ]"
          ></i>
        </a>
      </template>
      <template #end>
        <div class="flex items-center gap-4">
          <NuxtLink class="flex items-center" to="/chat">
            <i class="pi pi-comments text-lg"></i>
            <span class="ml-1">Советник</span>
          </NuxtLink>
          <Button 
            icon="pi pi-sign-out" 
            class="p-button-rounded p-button-text p-button-danger" 
            @click="logout" 
            aria-label="Выйти"
            tooltip="Выйти"
            tooltipPosition="bottom"
          />
        </div>
      </template>
    </Menubar>
  </header>
  <slot />
</template>

<script setup lang="ts">
import { API } from '~/constants/Api'

const items = ref([
  {
    label: 'Транзакции',
    icon: 'pi pi-wallet',
    items: [
      {
        label: 'Список транзакций',
        icon: 'pi pi-list',
        command: () => {
          return navigateTo('/')
        },
      },
      {
        label: 'Добавить транзакцию',
        icon: 'pi pi-plus',
        command: () => {
          return navigateTo('/transactions/add')
        },
      }
    ]
  },
  {
    label: 'Категории',
    icon: 'pi pi-tags',
    command: () => {
      return navigateTo('/category/list')
    },
  }
])

const logout = () => {
  navigateTo('/login')
}
</script>

<style scoped>
.p-menubar :deep(.p-menubar-end) {
  margin-left: auto;
}
</style>
