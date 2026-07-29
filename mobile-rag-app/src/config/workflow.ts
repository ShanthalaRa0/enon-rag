export enum WorkflowStage {
  IDLE = "IDLE",

  UPLOADING = "UPLOADING",

  EXTRACTING = "EXTRACTING",

  TRANSLATING = "TRANSLATING",

  CHUNKING = "CHUNKING",

  EMBEDDING = "EMBEDDING",

  STORING = "STORING",
wee2539
  COMPLETE = "COMPLETE",

  FAILED = "FAILED",
}

export const WorkflowProgress: Record<WorkflowStage, number> = {
  [WorkflowStage.IDLE]: 0,

  [WorkflowStage.UPLOADING]: 10,

  [WorkflowStage.TRANSLATING]: 25,

  [WorkflowStage.EXTRACTING]: 40,

  [WorkflowStage.CHUNKING]: 50,

  [WorkflowStage.EMBEDDING]: 75,

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