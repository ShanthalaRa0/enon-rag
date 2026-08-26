import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import { DocumentPickerAsset } from "expo-document-picker";

import { uploadDocument } from "@/services/upload";
import { WorkflowSocket } from "@/services/websocket";

// =========================================================
// Types
// =========================================================

export type UploadStatus =
  | "IDLE"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED";

export type UploadHistoryItem = {
  id: string;

  filename: string;

  size?: number;

  mimeType?: string;

  workflowId: string;

  status: UploadStatus;

  currentStage: string;

  progress: number;

  createdAt: string;

  completedAt?: string;

  error?: string;
};

// =========================================================
// Context Type
// =========================================================

type UploadContextType = {
  selectedFile: DocumentPickerAsset | null;

  setSelectedFile: (
    file: DocumentPickerAsset | null
  ) => void;

  uploadHistory: UploadHistoryItem[];

  uploadFile: (
    file: DocumentPickerAsset,
    overwrite?: boolean
  ) => Promise<void>;
};

// =========================================================
// Context
// =========================================================

const UploadContext =
  createContext<UploadContextType | null>(null);

// =========================================================
// Provider
// =========================================================

export function UploadProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  // -------------------------------------------------------
  // Selected file
  // -------------------------------------------------------

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<DocumentPickerAsset | null>(
    null
  );

  // -------------------------------------------------------
  // Upload history
  // -------------------------------------------------------

  const [
    uploadHistory,
    setUploadHistory,
  ] = useState<UploadHistoryItem[]>(
    []
  );

  // -------------------------------------------------------
  // WebSocket connections
  // -------------------------------------------------------

  const socketRefs =
    useRef<
      Record<string, WorkflowSocket>
    >({});

  // =======================================================
  // Create FormData
  // =======================================================

  function createFormData(
    file: DocumentPickerAsset
  ) {
    const formData = new FormData();

    formData.append(
      "file",
      {
        uri: file.uri,
        name: file.name,
        type:
          file.mimeType ??
          "application/octet-stream",
      } as any
    );

    return formData;
  }

  // =======================================================
  // Update one history item
  // =======================================================

  function updateHistoryItem(
    workflowId: string,
    updates: Partial<UploadHistoryItem>
  ) {
    setUploadHistory(
      (previous) =>
        previous.map((item) =>
          item.workflowId === workflowId
            ? {
                ...item,
                ...updates,
              }
            : item
        )
    );
  }

  // =======================================================
  // Disconnect one workflow
  // =======================================================

  function disconnectWorkflow(
    workflowId: string
  ) {
    const socket =
      socketRefs.current[workflowId];

    if (!socket) {
      return;
    }

    console.log(
      `[WS DISCONNECT] ${workflowId}`
    );

    try {
      socket.disconnect();
    } catch (error) {
      console.error(
        `[WS DISCONNECT ERROR] ${workflowId}`,
        error
      );
    }

    delete socketRefs.current[
      workflowId
    ];
  }

  // =======================================================
  // Upload
  // =======================================================

  async function uploadFile(
    file: DocumentPickerAsset,
    overwrite = false
  ): Promise<void> {
    const formData =
      createFormData(file);

    console.log(
      "[UPLOAD START]",
      file.name
    );

    console.log(
      "[UPLOAD OVERWRITE]",
      overwrite
    );

    try {
      // ---------------------------------------------------
      // Upload file to FastAPI
      // ---------------------------------------------------

      const response =
        await uploadDocument(
          formData,
          overwrite
        );

      console.log(
        "[UPLOAD RESPONSE]",
        response
      );

      const workflowId =
        response.workflow_id;

      console.log(
        "[WORKFLOW CREATED]",
        workflowId
      );

      // ---------------------------------------------------
      // Create history item
      // ---------------------------------------------------

      const historyItem: UploadHistoryItem = {
        id: workflowId,

        filename: file.name,

        size: file.size,

        mimeType: file.mimeType,

        workflowId,

        status: "RUNNING",

        currentStage: "UPLOADING",

        progress: 0,

        createdAt:
          new Date().toISOString(),
      };

      setUploadHistory(
        (previous) => [
          historyItem,
          ...previous,
        ]
      );

      // ---------------------------------------------------
      // Create WebSocket
      // ---------------------------------------------------

      const socket =
        new WorkflowSocket(
          workflowId
        );

      socketRefs.current[
        workflowId
      ] = socket;

      console.log(
        `[WS CREATED] ${workflowId}`
      );

      // ---------------------------------------------------
      // Connect WebSocket
      // ---------------------------------------------------

      socket.connect(

        // ON MESSAGE
        (event) => {
          console.log(
            `[WS EVENT RECEIVED] ${workflowId}`,
            JSON.stringify(
              event,
              null,
              2
            )
          );

          // =============================================
          // Pipeline started
          // =============================================

          if (
            event.type ===
            "PIPELINE_STARTED"
          ) {
            updateHistoryItem(
              workflowId,
              {
                status: "RUNNING",

                currentStage:
                  event.stage ??
                  "UPLOADING",

                progress:
                  event.progress ??
                  10,
              }
            );

            return;
          }

          // =============================================
          // Stage update
          // =============================================

          if (
            event.type ===
            "STAGE_UPDATE"
          ) {
            console.log(
              `[STAGE UPDATE] ${workflowId}`,
              event.stage,
              event.progress
            );

            updateHistoryItem(
              workflowId,
              {
                status: "RUNNING",

                currentStage:
                  event.stage,

                progress:
                  event.progress,
              }
            );

            return;
          }

          // =============================================
          // Pipeline completed
          // =============================================

          if (
            event.type ===
            "PIPELINE_COMPLETED"
          ) {
            console.log(
              `[WORKFLOW COMPLETED] ${workflowId}`
            );

            updateHistoryItem(
              workflowId,
              {
                status:
                  "COMPLETED",

                currentStage:
                  event.stage ??
                  "COMPLETE",

                progress: 100,

                completedAt:
                  new Date().toISOString(),
              }
            );

            disconnectWorkflow(
              workflowId
            );

            return;
          }

          // =============================================
          // Pipeline failed
          // =============================================

          if (
            event.type ===
            "PIPELINE_FAILED"
          ) {
            console.error(
              `[WORKFLOW FAILED] ${workflowId}`,
              event.error
            );

            updateHistoryItem(
              workflowId,
              {
                status: "FAILED",

                currentStage:
                  event.stage ??
                  "FAILED",

                progress:
                  event.progress ??
                  0,

                error:
                  event.error ??
                  "Workflow failed",
              }
            );

            disconnectWorkflow(
              workflowId
            );

            return;
          }

          // =============================================
          // Unknown event
          // =============================================

          console.log(
            `[UNKNOWN WS EVENT] ${workflowId}`,
            event
          );
        },

        // ON OPEN
        () => {
          console.log(
            `[WS OPEN] ${workflowId}`
          );
        },

        // ON CLOSE
        () => {
          console.log(
            `[WS CLOSE] ${workflowId}`
          );
        },

        // ON ERROR
        (error) => {
          console.error(
            `[WS ERROR] ${workflowId}`,
            error
          );
        }
      );
    } catch (error) {
      console.error(
        "[UPLOAD ERROR]",
        error
      );

      throw error;
    }
  }

  // =======================================================
  // Cleanup
  // =======================================================

  useEffect(() => {
    return () => {
      console.log(
        "[UPLOAD PROVIDER UNMOUNT]"
      );

      Object.entries(
        socketRefs.current
      ).forEach(
        ([workflowId, socket]) => {
          console.log(
            `[WS CLEANUP] ${workflowId}`
          );

          try {
            socket.disconnect();
          } catch (error) {
            console.error(
              `[WS CLEANUP ERROR] ${workflowId}`,
              error
            );
          }
        }
      );

      socketRefs.current = {};
    };
  }, []);

  // =======================================================
  // Provider
  // =======================================================

  return (
    <UploadContext.Provider
      value={{
        selectedFile,

        setSelectedFile,

        uploadHistory,

        uploadFile,
      }}
    >
      {children}
    </UploadContext.Provider>
  );
}

// =========================================================
// Hook
// =========================================================

export function useUpload() {
  const context =
    useContext(UploadContext);

  if (!context) {
    throw new Error(
      "useUpload must be used inside UploadProvider"
    );
  }

  return context;
}