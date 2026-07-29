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

export async function sendQuestion(
  question: string,
  topK: number = 5
) {
  console.log("Sending question...");
  console.log("question =", question);

  const response = await api.post(
    "/query",
    {
      question: question,
      top_k: topK,
    }
  );

  return response.data;
}