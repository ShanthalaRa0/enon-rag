export interface WorkflowEvent {

    workflow_id: string;

    type:
        | "PIPELINE_STARTED"
        | "STAGE_UPDATE"
        | "PIPELINE_COMPLETED"
        | "PIPELINE_FAILED";


    status:
        | "IDLE"
        | "RUNNING"
        | "COMPLETED"
        | "FAILED";


    stage: string;


    progress: number;


    message: string;


    error?: string;
}