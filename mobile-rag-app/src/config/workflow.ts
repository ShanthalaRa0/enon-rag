export enum WorkflowStage {
  IDLE = "IDLE",

  UPLOADING = "UPLOADING",

  EXTRACTING = "EXTRACTING",

  TRANSLATING = "TRANSLATING",

  CHUNKING = "CHUNKING",

  EMBEDDING = "EMBEDDING",

  STORING = "STORING",

  COMPLETE = "COMPLETE",

  FAILED = "FAILED",
}

export const WorkflowProgress: Record<WorkflowStage, number> = {
  [WorkflowStage.IDLE]: 0,

  [WorkflowStage.UPLOADING]: 10,

  [WorkflowStage.EXTRACTING]: 25,

  [WorkflowStage.TRANSLATING]: 50,

  [WorkflowStage.CHUNKING]: 70,

  [WorkflowStage.EMBEDDING]: 80,

  [WorkflowStage.STORING]: 90,

  [WorkflowStage.COMPLETE]: 100,

  [WorkflowStage.FAILED]: 100,
};

export const WorkflowLabels: Record<WorkflowStage, string> = {
  [WorkflowStage.IDLE]: "Waiting",

  [WorkflowStage.UPLOADING]: "Uploading document",

  [WorkflowStage.EXTRACTING]: "Extracting text",

  [WorkflowStage.TRANSLATING]: "Translating document",

  [WorkflowStage.CHUNKING]: "Creating chunks",

  [WorkflowStage.EMBEDDING]: "Generating embeddings",

  [WorkflowStage.STORING]: "Storing vectors",

  [WorkflowStage.COMPLETE]: "Completed",

  [WorkflowStage.FAILED]: "Failed",
};