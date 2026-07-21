import { API_URL } from "@/config/api";
import axios from "axios";

const apiRag = axios.create({
  baseURL: API_URL,
  timeout: 5000,
});

export default apiRag;