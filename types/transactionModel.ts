import * as yup from "yup";
import {requiredError} from "~/constants/defaultErrorMessages";

export const transactionSchema = yup.object({
  title: yup.string().required(requiredError).max(100, 'Максимальная длина 55 символов'),
  amount: yup.number().required(requiredError).min(0, 'Сумма должна быть больше 0').max(100000000, 'Слишком много'),
  category: yup.object().required(requiredError),
  datetime: yup.date().required(requiredError).max(new Date(), 'Дата не может быть в будущем'),
})


export interface TransactionModel extends yup.InferType<typeof transactionSchema> {}