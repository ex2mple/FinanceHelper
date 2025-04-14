import * as yup from 'yup'
import {passwordMaxLength, passwordMinLength} from '~/constants/authErrorMessages'
import {emailError, requiredError} from '~/constants/defaultErrorMessages'

const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

export const createUserSchema = yup.object({
    email: yup
        .string()
        .required(requiredError) // Сначала проверка на обязательность
        .matches(emailRegex, emailError) // Затем проверка по regex
        .max(100, 'Слишком длинный email'), // Затем по длине
    password: yup
        .string()
        .min(8, passwordMinLength)
        .max(50, passwordMaxLength)
        .required(requiredError),
    username: yup.string().required(requiredError).max(50, 'Слишком длинный никнейм'),
    gender: yup.string().oneOf(['Male', 'Female'], 'Недопустимое значение').required(requiredError), // Добавил сообщение для oneOf
    age: yup.number().positive('Возраст должен быть положительным').required(requiredError).min(14, 'Возраст должен быть не менее 14 лет'), // Уточнил сообщения
    salary: yup.number().positive('Зарплата должна быть положительной').required(requiredError).min(1, 'Зарплата должна быть больше 0').max(100000000, 'Слишком большая зарплата'),
})

export const loginUserSchema = yup.object({
    email: yup
        .string()
        .required(requiredError)
        .matches(emailRegex, emailError) // Используем regex
        .max(100, 'Слишком длинный email'),
    password: yup
        .string()
        .min(8, passwordMinLength)
        .max(50, passwordMaxLength)
        .required(requiredError),
})


export const editUserSchema = yup.object({
    email: yup
        .string()
        .required(requiredError)
        .matches(emailRegex, emailError) // Используем regex
        .max(100, 'Слишком длинный email'),
    password: yup // Пароль не обязателен при редактировании
        .string()
        .min(8, passwordMinLength)
        .max(50, passwordMaxLength)
        .nullable() // Позволяем быть null
        .transform((value) => (!!value ? value : null)), // Преобразуем пустую строку в null, если нужно
    // .optional() // Или так, если пустая строка не должна проходить min/max
    username: yup.string().required(requiredError).max(50, 'Слишком длинный никнейм'),
    gender: yup.string().oneOf(['Male', 'Female'], 'Недопустимое значение').required(requiredError),
    age: yup.number().positive('Возраст должен быть положительным').required(requiredError).min(14, 'Возраст должен быть не менее 14 лет'),
    salary: yup.number().positive('Зарплата должна быть положительной').required(requiredError).min(1, 'Зарплата должна быть больше 0').max(100000000, 'Слишком большая зарплата'),
})

export interface CreateUser extends yup.InferType<typeof createUserSchema> {
}

export interface LoginUser extends yup.InferType<typeof loginUserSchema> {
}

export interface EditUser extends yup.InferType<typeof editUserSchema> {
}
