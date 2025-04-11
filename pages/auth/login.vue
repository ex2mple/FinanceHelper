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

  try {
    const res = await instance.post('/auth/login', {
      email: data.values.email,
      password: data.values.password,
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
  <Toast position="top-right" />
  <div
    class="flex min-h-screen w-full items-center justify-center p-4"
  >
    <Card
      class="animate-fadein w-full max-w-md backdrop-blur-md shadow-lg border-0"
    >
      <template #title>
        <h1 class="text-3xl font-medium text-center mb-4">Добро пожаловать</h1>
      </template>
      <template #content>
        <Form
          @submit="onSubmit"
          v-slot="form"
          :resolver="resolver"
          :validateOnValueUpdate="false"
          :validateOnBlur="true"
          class="space-y-4"
        >
          <div>
            <span class="p-float-label">
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
            <span class="p-float-label">
              <label for="password">Пароль</label>
              <Password
                id="password"
                name="password"
                toggleMask
                :feedback="false"
                class="w-full"
                inputClass="w-full rounded-lg p-input-filled"
                :class="{'p-invalid': form.password?.invalid}"
                :inputStyle="{ width: '100%' }"
              />
            </span>
            <Message v-if="form.password?.invalid" severity="error" class="mt-2">
              {{ form.password.error.message }}
            </Message>
          </div>

          <div class="pt-4">
            <Button
              type="submit"
              label="Войти"
              class="w-full"
              rounded
              :loading="!!form.isSubmitting"
            />
          </div>

          <div class="text-center">
            <NuxtLink
              to="/auth/reg"
              class="hover:underline font-medium"
            >
              Создать аккаунт
            </NuxtLink>
          </div>

          <Divider align="center">
            <span class="0 px-2">или</span>
          </Divider>

          <Button
            type="button"
            class="w-full p-button-secondary"
            rounded
            @click="redirectToYandexAuth"
          >
            <div class="flex items-center justify-center gap-2">
              <img src="/assets/YaLogo.svg" width="24" height="24" alt="Логотип Яндекса" />
              <span>Войти через Яндекс</span>
            </div>
          </Button>
        </Form>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.animate-fadein {
  animation: fadeIn 0.7s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
