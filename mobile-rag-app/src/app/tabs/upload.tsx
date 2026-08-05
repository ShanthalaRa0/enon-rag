import { useEffect, useRef, useState } from "react";

import * as DocumentPicker from "expo-document-picker";

import { uploadDocument } from "@/services/upload";
import { WorkflowSocket } from "@/services/websocket";
import { useWorkflowSocket } from "@/hooks/useWorkflowSocket";

import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import UploadButton from "@/components/UploadButton";
import { Colors } from "@/theme";
import { DocumentPickerAsset } from "expo-document-picker";
import { logger } from "react-native-reanimated/lib/typescript/common/logger";

export default function UploadScreen() {
  const [selectedFile, setSelectedFile] =
    useState<DocumentPicker.DocumentPickerAsset | null>(null);

  const [uploading, setUploading] =
    useState(false);

  const [workflowId, setWorkflowId] =
    useState<string>();
    
  const event =
        useWorkflowSocket(workflowId);
  const socketRef =
    useRef<WorkflowSocket | null>(null);

  // -----------------------------
  // Workflow State
  // -----------------------------

  const [status, setStatus] = useState<
    "IDLE" | "RUNNING" | "COMPLETED" | "FAILED"
  >("IDLE");

  const [currentStage, setCurrentStage] =
    useState("Waiting...");

  const [progress, setProgress] =
    useState<number>(0);

  const [events, setEvents] = useState<any[]>([]);

  // -----------------------------
  // Pick File
  // -----------------------------

  async function pickDocument() {
    try {
      const result =
        await DocumentPicker.getDocumentAsync({
          multiple: false,
          copyToCacheDirectory: true,
        });

      if (result.canceled) {
        return;
      }

      const file = result.assets[0];

      setSelectedFile(file);

      // const data = new FormData();

      // data.append("file", {
      //   uri: file.uri,
      //   name: file.name,
      //   type:
      //     file.mimeType ??
      //     "application/octet-stream",
      // } as any);

      // setFormData(data);

      console.log("Selected File:", file);
      console.log("FormData Ready");
    } catch (error) {
      console.error(error);

      Alert.alert(
        "Error",
        "Unable to select file."
      );
    }
  }

  // -----------------------------
  // Upload
  // -----------------------------

  async function uploadFile(overwrite = false) {
     console.log("overwrite type:",typeof overwrite, overwrite);
    if (!selectedFile) return;

    const formData = createFormData(selectedFile);

    console.log("Uploading file with overwrite =", overwrite);

    try {
      setUploading(true);

      setStatus("RUNNING");
      setCurrentStage("Uploading...");
      setProgress(0);
      setEvents([]);

      const response =
        await uploadDocument(formData, overwrite);

      console.log(response);

      setWorkflowId(response.workflow_id);

      const socket =
        new WorkflowSocket(
          response.workflow_id
        );

      socketRef.current = socket;

      socket.connect((event) => {
        console.log(
          "WS EVENT:",
          JSON.stringify(event, null, 2)
        );

        setEvents((prev) => [
          ...prev,
          event,
        ]);

        switch (event.type) {
          case "STAGE_UPDATE":
            setStatus("RUNNING");
            setCurrentStage(event.stage);
            setProgress(event.progress);
            break;

          case "PIPELINE_COMPLETED":
            setStatus("COMPLETED");
            setCurrentStage(event.stage);
            setProgress(event.progress);
            break;

          case "PIPELINE_FAILED":
            setStatus("FAILED");
            Alert.alert("Workflow Failed", event.error);
            break;
        }
      });
    } catch (err: any) {
      console.log("UPLOAD ERROR:", err.response?.status, err.response?.data);

      // File already exists
      if (err.response?.status === 409) {
        Alert.alert(
          "File Already Exists",
          "This file is already stored. Do you want to overwrite it?",
          [
            {
              text: "Cancel",
              style: "cancel",
            },
            {
              text: "Overwrite",
              style: "destructive",
              onPress: () => {
                uploadFile(true);
              },
            },
          ]
        );
        return;
      }

      Alert.alert(
        "Upload Failed",
        "Unable to upload document."
      );

      setStatus("FAILED");
    } finally {
      setUploading(false);
    }
  }

  function createFormData(file: DocumentPickerAsset) {
    const fd = new FormData();

    fd.append("file", {
      uri: file.uri,
      name: file.name,
      type: file.mimeType ?? "application/octet-stream",
    } as any);

    return fd;
  }

  // -----------------------------
  // Cleanup
  // -----------------------------

  useEffect(() => {
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  // -----------------------------
  // UI
  // -----------------------------

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.title}>
        Upload Document
      </Text>

      <UploadButton
        title="Select File"
        onPress={pickDocument}
      />

      {selectedFile && (
        <>
          {/* File details */}
          <View style={styles.card}>
            <Text style={styles.label}>
              Name
            </Text>

            <Text style={styles.value}>
              {selectedFile.name}
            </Text>

            <Text style={styles.label}>
              Size
            </Text>

            <Text style={styles.value}>
              {(
                (selectedFile.size ??
                  0) / 1024
              ).toFixed(2)}{" "}
              KB
            </Text>

            <Text style={styles.label}>
              MIME Type
            </Text>

            <Text style={styles.value}>
              {selectedFile.mimeType}
            </Text>
          </View>

          {/* Upload button */}
          <UploadButton
            title={uploading ? "Uploading..." : "Upload"}
            onPress={() => uploadFile(false)}
            disabled={uploading}
          />

          {/* Workflow ID */}
          {workflowId && (
            <View style={styles.card}>
              <Text style={styles.label}>
                Workflow ID
              </Text>

              <Text style={styles.value}>
                {workflowId}
              </Text>
            </View>
          )}

          {/* Status */}
          <View style={styles.card}>
            <Text style={styles.label}>
              Workflow Status
            </Text>

            <Text style={styles.value}>
              {status}
            </Text>

            <Text style={styles.label}>
              Current Stage
            </Text>

            <Text style={styles.value}>
              {currentStage}
            </Text>

            <Text style={styles.label}>
              Progress
            </Text>

            <Text style={styles.value}>
              {progress}%
            </Text>
          </View>

          {/* Events */}
          <View style={styles.card}>
            <Text style={styles.label}>
              Live Events
            </Text>

            {events.length === 0 && (
              <Text style={styles.value}>
                Waiting for workflow updates...
              </Text>
            )}

            {events.map((event, index) => (
              <Text
                key={index}
                style={styles.value}
              >
                {JSON.stringify(event)}
              </Text>
            ))}
          </View>

          {/* Current event */}
          <View>
            {event && (
              <>
                <Text>{event.type}</Text>
                <Text>{event.workflow_id}%</Text>
              </>
            )}
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },

  content: {
    padding: 20,
    gap: 20,
  },

  title: {
    fontSize: 24,
    fontWeight: "700",
    color: Colors.foreground,
  },

  card: {
    backgroundColor: Colors.sidebar,
    padding: 16,
    borderRadius: 10,
    gap: 8,
  },

  label: {
    color: Colors.primary,
    fontWeight: "600",
  },

  value: {
    color: Colors.foreground,
  },
});