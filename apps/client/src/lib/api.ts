import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// // Request interceptor
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem("access_token");

//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }

//   return config;
// });

// // Response interceptor
// api.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     if (error.response?.status === 401) {
//       // handle refresh token logic here later
//       console.log("Unauthorized - redirect or refresh token");
//     }

//     return Promise.reject(error);
//   },
// );
