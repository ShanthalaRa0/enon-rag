import api from "@/services/api";

export async function uploadDocument(formData: FormData, overwrite: boolean) {
  console.log("Uploading...");
  console.log("api =", api);
  // Remove old values
  formData.delete("overwrite");
  console.log("formData =", formData);
   // Add exactly one value
  formData.append("overwrite", String(overwrite));
  try {
    const response = await api.post(
      "/upload",
      formData,
      // {
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //   },
      // }
    );
    console.log("Upload response:", response.status);
    console.log("Upload response data:", response.data);
  
    return response.data;
  } catch (error: any) {
    console.log("UPLOAD REQUEST FAILED");
    console.log("status:", error.response?.status);
    console.log("data:", error.response?.data);
    console.log("message:", error.message);

    throw error;
  }
}

