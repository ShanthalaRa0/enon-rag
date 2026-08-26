import { useState } from "react";

import * as DocumentPicker from "expo-document-picker";

import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import UploadButton from "@/components/UploadButton";
import { Colors } from "@/theme";
import { useUpload } from "@/context/UploadContext";

export default function UploadScreen() {
  const {
    selectedFile,
    setSelectedFile,
    uploadFile,
  } = useUpload();

  // ---------------------------------------------
  // Select file
  // ---------------------------------------------

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

      console.log(
        "Selected File:",
        file
      );

      setSelectedFile(file);
    } catch (error) {
      console.error(
        "Document picker error:",
        error
      );

      Alert.alert(
        "Error",
        "Unable to select file."
      );
    }
  }

  // ---------------------------------------------
  // Upload
  // ---------------------------------------------

  async function handleUpload() {
    if (!selectedFile) {
      return;
    }
    if (selectedFile.size === 0) {
      Alert.alert("Invalid File", "The selected file is empty.");
      return;
    }
    const fileName = selectedFile.name ?? "";
    const extension = fileName.split(".").pop()?.toLowerCase();

    const supportedExtensions = [
      "pdf",
      "doc",
      "docx",
      "xls",
      "xlsx",
      "ppt",
      "pptx",
      "jpg",
      "jpeg",
      "png",
      "gif",
    ];
    if (!extension || !supportedExtensions.includes(extension)) {
      Alert.alert(
        "Unsupported File Type",
        "Please select a PDF, Word, Excel, PowerPoint, or image file."
      );
      return;
    }

    try {
      await uploadFile(
        selectedFile,
        false
      );

      /*
       * IMPORTANT:
       *
       * uploadFile() only waits until the backend
       * creates the workflow.
       *
       * Celery continues processing in the backend.
       *
       * The Upload tab is therefore immediately
       * ready for another file.
       */

      setSelectedFile(null);
    } catch (err: any) {
      console.log(
        "UPLOAD ERROR:",
        err?.response?.status,
        err?.response?.data
      );

      // -----------------------------------------
      // File already exists
      // -----------------------------------------

      if (
        err?.response?.status === 409
      ) {
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
              onPress: async () => {
                try {
                  await uploadFile(
                    selectedFile,
                    true
                  );

                  // Ready for another file
                  setSelectedFile(null);
                } catch (overwriteError: any) {
                  console.log(
                    "OVERWRITE ERROR:",
                    overwriteError
                  );

                  Alert.alert(
                    "Upload Failed",
                    "Unable to overwrite the document."
                  );
                }
              },
            },
          ]
        );

        return;
      }

      Alert.alert(
        "Upload Failed",
        "Unable to upload the document."
      );
    }
  }

  // ---------------------------------------------
  // UI
  // ---------------------------------------------

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
    >
      <Text style={styles.title}>
        Upload Document
      </Text>

      {!selectedFile && (
        <UploadButton
          title="Select File"
          onPress={pickDocument}
        />
      )}

      {selectedFile && (
        <>
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
                (selectedFile.size ?? 0) / 1024
              ).toFixed(2)}{" "}
              KB
            </Text>

            <Text style={styles.label}>
              MIME Type
            </Text>

            <Text style={styles.value}>
              {selectedFile.mimeType ?? "Unknown"}
            </Text>
          </View>

          <UploadButton
            title="Upload"
            onPress={handleUpload}
          />

          <UploadButton
            title="Select Another File"
            onPress={pickDocument}
          />
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor:
      Colors.background,
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
    backgroundColor:
      Colors.sidebar,
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