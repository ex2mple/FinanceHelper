import * as yup from 'yup'
import { passwordMaxLength, passwordMinLength } from '~/constants/authErrorMessages'
import { emailError, requiredError } from '~/constants/defaultErrorMessages'

export const createUserSchema = yup.object({
  email: yup.string().email(emailError).required(requiredError),
  password: yup
    .string()
    .min(8, passwordMinLength)
    .max(20, passwordMaxLength)
    .required(requiredError),
  first_name: yup.string().required(requiredError),
})

export const loginUserSchema = yup.object({
  email: yup.string().email(emailError).required(requiredError),
  password: yup.string().required(requiredError).max(20, passwordMaxLength),
})

export interface CreateUser extends yup.InferType<typeof createUserSchema> {}
export interface LoginUser extends yup.InferType<typeof loginUserSchema> {}
