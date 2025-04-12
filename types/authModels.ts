import * as yup from 'yup'
import { passwordMaxLength, passwordMinLength } from '~/constants/authErrorMessages'
import { emailError, requiredError } from '~/constants/defaultErrorMessages'

export const createUserSchema = yup.object({
  email: yup.string().email(emailError).required(requiredError).max(100, 'Слишком длинный email'),
  firstName: yup.string().required(requiredError).max(100, 'Слишком длинное имя'),
  password: yup
    .string()
    .min(8, passwordMinLength)
    .max(50, passwordMaxLength)
    .required(requiredError),
  username: yup.string().required(requiredError).max(50, 'Слишком длинный никнейм'),
  gender: yup.string().oneOf(['Male', 'Female']).required(requiredError),
  age: yup.number().positive('Должно быть больше 13').required(requiredError).min(14, 'Возраст должен быть больше 13'),
  salary: yup.number().positive('Должно быть больше 0').required(requiredError).min(1, 'Зарплата должна быть больше 0').max(100000000, 'Слишком большая зарплата'),
})

export const loginUserSchema = yup.object({
  email: yup.string().email(emailError).required(requiredError).max(100, 'Слишком длинный email'),
  password: yup
  .string()
  .min(8, passwordMinLength)
  .max(50, passwordMaxLength)
  .required(requiredError),
})

export interface CreateUser extends yup.InferType<typeof createUserSchema> {}
export interface LoginUser extends yup.InferType<typeof loginUserSchema> {}
