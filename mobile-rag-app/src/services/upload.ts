import api from "@/services/api";

export async function uploadDocument(formData: FormData, overwrite: boolean) {
  console.log("Uploading...");
  console.log("api =", api);
  // Remove old values
  formData.delete("overwrite");
  console.log("formData =", formData);
   // Add exactly one value
  formData.append("overwrite", String(overwrite));
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

