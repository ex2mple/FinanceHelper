<script setup lang="ts">
import {loginUserSchema} from '~/types/authModels'
import {yupResolver} from '@primevue/forms/resolvers/yup'
import {useToast} from '#imports'
import instance from '~/axiosInstance'

definePageMeta({
  requireAuth: false,
  layout: false,
})

const resolver = yupResolver(loginUserSchema)
const toast = useToast()

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

  const formData = new FormData()
  formData.set('username', data.values.email)
  formData.set('password', data.values.password)

  try {
    const res = await instance.post('/auth/token', formData, {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
    navigateTo('/')
  } catch (err: any) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    console.error(errorMessage)
    displayErrorToast(err.response.data?.detail)
  }
}
</script>

<template>
  <Toast position="top-right"/>
  <div
      class="flex min-h-screen w-full items-center justify-center p-4"
  >
    <Card
        class="animate-fadein w-full max-w-md backdrop-blur-md shadow-lg border-0 "
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
                :loading="!!form.isSubmitting"
            />
          </div>

          <div class="text-center">
            <NuxtLink
                to="/register"
                class="hover:underline font-medium"
            >
              Создать аккаунт
            </NuxtLink>
          </div>
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
