<script setup lang="ts">
import { loginUserSchema } from '~/types/authModels'
import { yupResolver } from '@primevue/forms/resolvers/yup'
import { useToast } from '#imports'
import { API } from '~/constants/Api'
import instance from '~/axiosInstance'

definePageMeta({
  requireAuth: false,
  layout: false,
})

const resolver = yupResolver(loginUserSchema)
const toast = useToast()

const redirectToYandexAuth = () => {
  window.location.href = `${API}/yandex/login`
}

const displayErrorToast = (msg: string) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка авторизации',
    detail: msg,
    life: 2500,
  })
}

const onSubmit = async (data: any) => {
  if (!data.valid) {
    return
  }

  console.log(data)
  try {
    const res = await instance.post('/auth/login', {
      email: data.states.login.value,
      password: data.states.password.value,
    })
    localStorage.setItem('user', JSON.stringify(res.data))
    localStorage.setItem('user_id', res.data.user.id)
    navigateTo('/')
  } catch (err: any) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    console.error(errorMessage)
    displayErrorToast(err.response.data?.detail)
  }
}
</script>

<template>
  <Toast></Toast>
  <div
    class="flex h-screen w-screen items-center justify-center bg-[linear-gradient(-225deg,var(--p-primary-500),var(--p-primary-700)_48%,var(--p-primary-800))] px-6 py-20 md:px-12 lg:px-20 dark:bg-[linear-gradient(-225deg,var(--p-primary-400),var(--p-primary-600)_48%,var(--p-primary-800))]"
  >
    <Form
      @submit="onSubmit"
      v-slot="form"
      :resolver="resolver"
      class="animate-fadein rounded-xl bg-[rgba(255,255,255,0.1)] p-12 text-center shadow backdrop-blur-md lg:w-[30rem]"
    >
      <div class="mb-12 text-4xl font-medium text-white">Добро пожаловать</div>
      <div class="mb-6">
        <InputText
          type="text"
          name="login"
          class="!block !w-full !appearance-none !rounded-full !bg-white/10 !p-4 !text-xl placeholder:!text-white/40"
          placeholder="Email"
        />
        <Message
          v-if="form.login?.invalid"
          size="small"
          severity="error"
          variant="simple"
          class="ml-4"
        >
          {{ form.login.error.message }}
        </Message>
      </div>
      <div class="mb-6">
        <Password
          toggleMask
          :feedback="false"
          name="password"
          inputClass="!appearance-none placeholder:!text-white/40 !p-4 !w-full !outline-0 !text-xl !bg-white/10 !rounded-full"
          class="w-full"
          placeholder="Пароль"
        />
        <Message
          v-if="form.password?.invalid"
          size="small"
          severity="error"
          variant="simple"
          class="ml-4"
        >
          {{ form.password.error.message }}
        </Message>
      </div>

      <button
        type="submit"
        class="max-w-50 mb-4 w-full cursor-pointer appearance-none rounded-full border-0 bg-white/30 p-4 text-xl font-medium text-white/80 outline-0 transition-colors duration-150 hover:bg-white/40 active:bg-white/20"
      >
        Войти
      </button>
      <NuxtLink
        to="/auth/reg"
        class="mb-4 block cursor-pointer text-center font-medium text-white hover:underline"
        >Создать аккаунт</NuxtLink
      >
      <hr class="mx-auto mb-2 h-1 w-48 rounded-sm border-0 bg-gray-100" />
      <span class="!text-white/40">или</span>
      <button
        type="button"
        @click="redirectToYandexAuth"
        class="max-w-50 mt-4 w-full cursor-pointer appearance-none rounded-full border-0 bg-white/30 p-4 text-xl font-medium text-white/80 outline-0 transition-colors duration-150 hover:bg-white/40 active:bg-white/20"
      >
        <div class="flex items-center justify-center gap-4">
          <img src="/assets/YaLogo.svg" width="30px" height="30px" alt="Логотип Яндекса" /> Войти
          через Яндекс
        </div>
      </button>
    </Form>
  </div>
</template>
<style scoped>
.animate-fadein {
  animation: fadeIn 0.7s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(50px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
