import api from "@/services/api";

export async function uploadDocument(formData: FormData, overwrite: boolean,
  workflowId: string
) {
  console.log("Uploading...");
  console.log("api =", api);
  console.log("workflowId =", workflowId);
  // Remove old values
  formData.delete("overwrite");
  formData.delete("workflow_id");
  console.log("formData =", formData);
   // Add exactly one value
  formData.append("overwrite", String(overwrite));
  formData.append("workflow_id", workflowId);
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

