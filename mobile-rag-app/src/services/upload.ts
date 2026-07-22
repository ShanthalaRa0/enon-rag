import api from "@/services/api";

export async function uploadDocument(formData: FormData) {
  console.log("Uploading...");
  console.log("api =", api);
  console.log("formData =", formData);
  const response = await api.post(
    "/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}