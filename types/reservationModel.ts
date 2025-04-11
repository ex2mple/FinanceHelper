import * as yup from 'yup'
import { requiredError } from '~/constants/defaultErrorMessages'

export const reservationSchema = yup.object({
  id: yup.string().required(requiredError),
  user_id: yup.string().required(requiredError),
  seat_id: yup.string().required(requiredError),
  start: yup.date().required(requiredError),
  end: yup.date().required(requiredError),
  status: yup.string().required(requiredError),
  seat_name: yup.string().required(requiredError),
})

export interface ReservationModel extends yup.InferType<typeof reservationSchema> {}
