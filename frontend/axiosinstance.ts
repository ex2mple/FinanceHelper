import axios from 'axios'
import { API } from '~/constants/Api'

const instance = axios.create({
  baseURL: API,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

export default instance