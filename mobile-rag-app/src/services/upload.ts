import api from "@/services/api";

export async function uploadDocument(formData: FormData, overwrite: boolean,folder: string,
  workflowId: string
) {
  console.log("Uploading...");
  console.log("api =", api);
  console.log("formData =", formData);

  console.log("workflowId =", workflowId);
  console.log("folder =", folder);
  // Remove old values
  formData.delete("overwrite");
  formData.delete("workflow_id");
  formData.delete("folder");
  console.log("formData =", formData);
  console.log("folder =", folder);
   // Add exactly one value
  formData.append("overwrite", String(overwrite));
  formData.append("workflow_id", workflowId);
  formData.append("folder", folder);
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

