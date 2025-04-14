import * as yup from 'yup'
import { emailError, requiredError } from '~/constants/defaultErrorMessages'

export const userSchema = yup.object({
  id: yup.string().nonNullable(),
  role: yup.string().nonNullable(),
  email: yup.string().email(emailError).required(requiredError),
  first_name: yup.string().required(requiredError),
  verified: yup.boolean().required(requiredError),
})

export interface UserModel extends yup.InferType<typeof userSchema> {}
