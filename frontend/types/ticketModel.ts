import * as yup from 'yup'
import { requiredError } from '~/constants/defaultErrorMessages'

export const ticketSchema = yup.object({
  id: yup.string().required(requiredError),
  status: yup.string().required(requiredError),
  seat_id: yup.string().required(requiredError),
  user_id: yup.string().required(requiredError),
  theme: yup.string().required(requiredError),
  message: yup.string().required(requiredError),
  made_on: yup.date().required(requiredError),
  reservation_id: yup.string().required(requiredError),
  seat_name: yup.string().required(requiredError),
})

export const ticketCreateSchema = yup.object({
  message: yup.string().required(requiredError),
  theme: yup.object().required(requiredError),
})

export interface TicketModel extends yup.InferType<typeof ticketSchema> {}

export interface TicketCreateModel extends yup.InferType<typeof ticketCreateSchema> {}
