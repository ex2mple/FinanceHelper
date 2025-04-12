<script setup lang="ts">
import {createUserSchema, type CreateUser} from '~/types/authModels'
import {yupResolver} from '@primevue/forms/resolvers/yup'
import {useToast} from '#imports'
import {API} from '~/constants/Api'
import instance from '~/axiosinstance'

definePageMeta({
  requireAuth: false,
  layout: false,
})

const resolver = yupResolver(createUserSchema)
const toast = useToast()

const redirectToYandexAuth = () => {
  window.location.href = `${API}/yandex/login`
}

const displayErrorToast = (msg: string) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка регистрации',
    detail: msg,
    life: 2500,
  })
}

const onSubmit = async (data: { valid: Boolean; values: CreateUser }) => {
  if (!data.valid) {
    displayErrorToast('Проверьте правильность введенных данных')
    return
  }

  try {
    console.log(data.values)
    instance.post('/users/', data.values)
        .then(() => {
          const formData = new FormData()
          formData.set('username', data.values.email)
          formData.set('password', data.values.password)
          instance.post('/auth/token', formData, {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
              .then(() => {
                navigateTo('/')
              })
        })
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
            <span class="flex flex-col gap-1">
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
            <span class="flex flex-col gap-1">
              <label for="first_name">Ваше имя</label>
              <InputText
                  id="username"
                  type="text"
                  name="username"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.username?.invalid}"
              />
            </span>
            <Message v-if="form.username?.invalid" severity="error" class="mt-2">
              {{ form.username.error.message }}
            </Message>
          </div>

          <div>
            <span class="flex flex-col gap-1">
              <label for="password">Пароль</label>
              <Password
                  id="password"
                  name="password"
                  toggleMask
                  :feedback="true"
                  class="w-full"
                  inputClass="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.password?.invalid}"
                  :weakLabel="'Слабый'"
                  :mediumLabel="'Средний'"
                  :strongLabel="'Сильный'"
                  :inputStyle="{ width: '100%' }"
              />
            </span>
            <Message v-if="form.password?.invalid" severity="error" class="mt-2">
              {{ form.password.error.message }}
            </Message>
          </div>

          <div>
            <label for="gender" class="block text-white mb-1">Пол</label>
            <div class="flex justify-content-center">
              <SelectButton
                  id="gender"
                  name="gender"
                  :options="[
                  { label: 'Мужской', value: 'Male' },
                  { label: 'Женский', value: 'Female' },
                ]"
                  optionLabel="label"
                  optionValue="value"
                  :class="{'p-invalid': form.gender?.invalid}"
              />
            </div>
            <Message v-if="form.gender?.invalid" severity="error" class="mt-2">
              {{ form.gender.error.message }}
            </Message>
          </div>

          <div>
            <span class="flex flex-col gap-1">
              <label for="age">Возраст</label>
              <InputNumber
                  id="age"
                  name="age"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.age?.invalid}"
                  :min="0"
              />
            </span>
            <Message v-if="form.age?.invalid" severity="error" class="mt-2">
              {{ form.age.error.message }}
            </Message>
          </div>

          <div>
            <span class="flex flex-col gap-1">
              <label for="salary">Зарплата</label>
              <InputNumber
                  id="salary"
                  name="salary"
                  mode="currency"
                  currency="RUB"
                  locale="ru-RU"
                  class="w-full  rounded-lg p-input-filled"
                  :class="{'p-invalid': form.salary?.invalid}"
                  :min="0"
              />
            </span>
            <Message v-if="form.salary?.invalid" severity="error" class="mt-2">
              {{ form.salary.error.message }}
            </Message>
          </div>

          <div class="pt-4">
            <Button
                type="submit"
                label="Зарегистрироваться"
                class="w-full"
                :loading="!!form.isSubmitting"
            />
          </div>

          <div class="text-center">
            <NuxtLink
                to="/login"
                class="text-white hover:underline font-medium"
            >
              Уже есть аккаунт
            </NuxtLink>
          </div>

          <Divider align="center">
            <span class="text-white/60 px-2">или</span>
          </Divider>

          <Button
              type="button"
              class="w-full p-button-secondary"
              @click="redirectToYandexAuth"
          >
            <div class="flex items-center justify-center gap-2">
              <img src="/assets/YaLogo.svg" width="24" height="24" alt="Логотип Яндекса"/>
              <span class="flex flex-col gap-1">Войти через Яндекс</span>
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