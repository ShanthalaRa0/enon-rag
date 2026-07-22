import { WorkflowStage } from "@/config/workflow";

export interface WorkflowMessage {
  workflow_id: string;

  stage: WorkflowStage;

  progress: number;

  status: "RUNNING" | "SUCCESS" | "FAILED";

  message: string;
}