import { useEffect, useRef, useState } from "react";

import * as DocumentPicker from "expo-document-picker";

import { uploadDocument } from "@/services/upload";

import { WorkflowSocket } from "@/services/websocket";

import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import UploadButton from "@/components/UploadButton";
import { Colors } from "@/theme";

export default function UploadScreen() {

  const [selectedFile, setSelectedFile] =
    useState<DocumentPicker.DocumentPickerAsset | null>(
      null
    );

  const [formData, setFormData] =
    useState<FormData | null>(null);
  
  const [uploading, setUploading] = useState(false);

  const [workflowId, setWorkflowId] =
    useState<string | null>(null);

  const socketRef =
    useRef<WorkflowSocket | null>(null);

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

      const data = new FormData();

      data.append("file", {
        uri: file.uri,
        name: file.name,
        type:
          file.mimeType ??
          "application/octet-stream",
      } as any);

      setFormData(data);

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

  async function uploadFile() {
    if (!formData) {
      return;
    }

    try {
      setUploading(true);

      const response = await uploadDocument(
        formData
      );

      console.log(response);

      setWorkflowId(response.workflow_id);

      const socket = new WorkflowSocket(
        response.workflow_id
      );

      socketRef.current = socket;

      socket.connect((event) => {
        console.log(
          "Workflow Event",
          event
        );

        switch (event.type) {
          case "STAGE_UPDATE":
            console.log(
              event.stage,
              event.progress
            );
            break;

          case "PIPELINE_COMPLETED":
            console.log("Completed");
            break;

          case "PIPELINE_FAILED":
            console.log(event.error);
            break;
        }
      });

    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  }

  useEffect(() => {
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

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
        <View style={styles.card}>
          <Text style={styles.label}>Name</Text>

          <Text style={styles.value}>
            {selectedFile.name}
          </Text>

          <Text style={styles.label}>Size</Text>

          <Text style={styles.value}>
            {((selectedFile.size ?? 0) / 1024).toFixed(2)} KB
          </Text>

          <Text style={styles.label}>MIME Type</Text>

          <Text style={styles.value}>
            {selectedFile.mimeType}
          </Text>
        </View>

        <UploadButton
          title={
            uploading
              ? "Uploading..."
              : "Upload"
          }
          onPress={uploadFile}
          disabled={uploading}
        />
      </>
    )}

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