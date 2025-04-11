<template>
  <div>
    <p>Авторизация проходит, пожалуйста, подождите...</p>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import instance from '~/axiosInstance'

definePageMeta({
  requireAuth: false,
})

const router = useRouter()
const route = useRoute()

onMounted(async () => {
  const token = route.query.access_token
  if (token) {
    try {
      const res = await instance.get('/user/me', {})
      if (!res.data) {
        console.warn('Нет данных пользователя:', res)
        return navigateTo('/auth/login')
      }
      localStorage.setItem(
        'user',
        JSON.stringify({
          user: res.data,
        })
      )
      if (process.client) {
        localStorage.setItem('user_id', res.data.id)
      }
      return await navigateTo('/')
    } catch (err) {
      console.error('Ошибка проверки аутентификации:', err)
      return navigateTo('/auth/login')
    }
  } else {
    console.error('Токен не найден в параметрах')
  }
})
</script>
