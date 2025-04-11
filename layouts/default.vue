<template>
  <header>
    <Menubar :model="items">
      <template #item="{ item, props, hasSubmenu, root }">
        <a v-ripple class="flex items-center" v-bind="props.action">
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
        <NuxtLink class="flex items-center gap-2" to="/">
          <Avatar :image="API + '/avatar'" shape="circle" />
        </NuxtLink>
      </template>
    </Menubar>
  </header>
  <slot />
</template>

<script setup lang="ts">
import { API } from '~/constants/Api'

const items = ref([
  {
    label: 'Главная',
    command: () => {
      return navigateTo('/')
    },
  },
])
</script>
