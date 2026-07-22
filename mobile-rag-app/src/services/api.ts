import axios from "axios";

import { API_URL } from "@/config/api";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

export default api;