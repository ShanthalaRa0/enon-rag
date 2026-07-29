import api from "@/services/api";

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