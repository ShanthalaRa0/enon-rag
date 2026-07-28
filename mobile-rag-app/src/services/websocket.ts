import { WS_URL } from "@/config/api";

export type WorkflowEvent =
  | {
      workflow_id: string;
      type: "STAGE_UPDATE";
      stage: string;
      progress: number;
    }
  | {
      workflow_id: string;
      type: "PIPELINE_COMPLETED";
      stage: "FINISHED";
      progress: 100;
    }
  | {
      workflow_id: string;
      type: "PIPELINE_FAILED";
      error: string;
    };

export type WorkflowEventHandler = (
  event: WorkflowEvent
) => void;

export class WorkflowSocket {
  private socket?: WebSocket;

  private workflowId: string;

  constructor(workflowId: string) {
    this.workflowId = workflowId;
  }

  connect(
    onMessage: WorkflowEventHandler,
    onOpen?: () => void,
    onClose?: () => void,
    onError?: (error: Event) => void
  ) {
    this.socket = new WebSocket(
      `${WS_URL}/workflow/${this.workflowId}`
    );

    this.socket.onopen = () => {
      console.log(
        "[WebSocket] Connected:",
        this.workflowId
      );

      onOpen?.();
    };

    this.socket.onmessage = (event) => {
      try {
        const payload: WorkflowEvent =
          JSON.parse(event.data);

        console.log(
          "[WebSocket] Event:",
          payload
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
        "[WebSocket] Error",
        event
      );

      onError?.(event);
    };

    this.socket.onclose = () => {
      console.log(
        "[WebSocket] Closed"
      );

      onClose?.();
    };
  }

  disconnect() {
    this.socket?.close();

    this.socket = undefined;
  }

  isConnected() {
    return (
      this.socket?.readyState ===
      WebSocket.OPEN
    );
  }

  send(data: unknown) {
    if (!this.isConnected()) {
      return;
    }

    this.socket?.send(
      JSON.stringify(data)
    );
  }
}