import { WS_URL } from "@/config/api";

// =========================================================
// Workflow Event
// =========================================================

export type WorkflowEvent =
  | {
      workflow_id: string;

      type: "PIPELINE_STARTED";

      stage?: string;

      progress?: number;

      status?: "RUNNING";

      message?: string;
    }
  | {
      workflow_id: string;

      type: "STAGE_UPDATE";

      stage: string;

      progress: number;

      status?: "RUNNING";

      message?: string;
    }
  | {
      workflow_id: string;

      type: "PIPELINE_COMPLETED";

      stage: string;

      progress: number;

      status?: "COMPLETED";

      message?: string;
    }
  | {
      workflow_id: string;

      type: "PIPELINE_FAILED";

      stage?: string;

      progress?: number;

      status?: "FAILED";

      message?: string;

      error?: string;
    };

// =========================================================
// Event Handler
// =========================================================

export type WorkflowEventHandler = (
  event: WorkflowEvent
) => void;

// =========================================================
// Workflow Socket
// =========================================================

export class WorkflowSocket {
  private socket?: WebSocket;

  private workflowId: string;

  constructor(workflowId: string) {
    this.workflowId = workflowId;
  }

  // =======================================================
  // Connect
  // =======================================================

  // =======================================================
// Connect
// =======================================================

connect(
  onMessage: WorkflowEventHandler,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (error: Event) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const url =
      `${WS_URL}/workflow/${this.workflowId}`;

    console.log(
      "[WebSocket] Connecting:",
      url
    );

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log(
        "[WebSocket] Connected:",
        this.workflowId
      );

      onOpen?.();

      // Resolve only after WebSocket is actually OPEN
      resolve();
    };

    this.socket.onmessage = (event) => {
      try {
        const payload: WorkflowEvent =
          JSON.parse(event.data);

        console.log(
          "[WebSocket] Event:",
          JSON.stringify(
            payload,
            null,
            2
          )
        );

        onMessage(payload);
      } catch (err) {
        console.error(
          "[WebSocket] Invalid message",
          err
        );
      }
    };

    this.socket.onerror = (event) => {
      console.error(
        "[WebSocket] Error:",
        event
      );

      onError?.(event);

      // Reject connection promise
      reject(
        new Error(
          `WebSocket connection failed for workflow ${this.workflowId}`
        )
      );
    };

    this.socket.onclose = (event) => {
      console.log(
        "[WebSocket] Closed:",
        this.workflowId
      );

      console.log(
        "Code:",
        event.code
      );

      console.log(
        "Reason:",
        event.reason
      );

      console.log(
        "Clean:",
        event.wasClean
      );

      onClose?.();
    };
  });
}

  // =======================================================
  // Disconnect
  // =======================================================

  disconnect() {
    if (this.socket) {
      console.log(
        "[WebSocket] Disconnecting:",
        this.workflowId
      );

      this.socket.close();

      this.socket = undefined;
    }
  }

  // =======================================================
  // Is Connected
  // =======================================================

  isConnected() {
    return (
      this.socket?.readyState ===
      WebSocket.OPEN
    );
  }

  // =======================================================
  // Send
  // =======================================================

  send(data: unknown) {
    if (!this.isConnected()) {
      console.warn(
        "[WebSocket] Cannot send. Socket is not connected."
      );

      return;
    }

    this.socket?.send(
      JSON.stringify(data)
    );
  }
}