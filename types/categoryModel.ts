import * as yup from 'yup'
import { requiredError } from '~/constants/defaultErrorMessages'

export const categorySchema = yup.object({
  id: yup.number().optional(),
  name: yup.string().required(requiredError),
  color: yup.string().required(requiredError),
  userId: yup.string().optional()
})

export interface CategoryModel extends yup.InferType<typeof categorySchema> {}