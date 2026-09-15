import { useState } from "react";

import * as DocumentPicker from "expo-document-picker";

import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
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
  // Folder state
  // ---------------------------------------------

  const [folders, setFolders] = useState<string[]>([
    "documents",
  ]);

  const [selectedFolder, setSelectedFolder] =
    useState<string>("documents");

  const [showFolderSelector, setShowFolderSelector] =
    useState(false);

  const [showCreateFolder, setShowCreateFolder] =
    useState(false);

  const [newFolderName, setNewFolderName] =
    useState("");

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
  // Create folder
  // ---------------------------------------------

  function createFolder() {
    const folder = newFolderName.trim();

    if (!folder) {
      Alert.alert(
        "Invalid Folder",
        "Please enter a folder name."
      );
      return;
    }

    if (
      folder === "." ||
      folder === ".." ||
      folder.includes("/") ||
      folder.includes("\\")
    ) {
      Alert.alert(
        "Invalid Folder",
        "Folder name cannot contain / or \\."
      );
      return;
    }

    const exists = folders.some(
      (item) =>
        item.toLowerCase() ===
        folder.toLowerCase()
    );

    if (exists) {
      Alert.alert(
        "Folder Exists",
        "A folder with this name already exists."
      );
      return;
    }

    setFolders((current) => [
      ...current,
      folder,
    ]);

    setSelectedFolder(folder);
    setNewFolderName("");
    setShowCreateFolder(false);
    setShowFolderSelector(false);

    console.log(
      "[FOLDER CREATED]",
      folder
    );
  }

  // ---------------------------------------------
  // Upload
  // ---------------------------------------------

  async function handleUpload() {
    if (!selectedFile) {
      return;
    }

    if (selectedFile.size === 0) {
      Alert.alert(
        "Invalid File",
        "The selected file is empty."
      );
      return;
    }

    const fileName =
      selectedFile.name ?? "";

    const extension =
      fileName
        .split(".")
        .pop()
        ?.toLowerCase();

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

    if (
      !extension ||
      !supportedExtensions.includes(
        extension
      )
    ) {
      Alert.alert(
        "Unsupported File Type",
        "Please select a PDF, Word, Excel, PowerPoint, or image file."
      );
      return;
    }

    try {
      console.log(
        "[UPLOAD]",
        {
          filename: selectedFile.name,
          folder: selectedFolder,
        }
      );

      await uploadFile(
        selectedFile,
        false,
        selectedFolder
      );

      setSelectedFile(null);
      setSelectedFolder("documents");

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
          `This file already exists in "${selectedFolder}". Do you want to overwrite it?`,
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
                    true,
                    selectedFolder
                  );

                  setSelectedFile(null);
                  setSelectedFolder(
                    "documents"
                  );

                } catch (
                  overwriteError: any
                ) {
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
      contentContainerStyle={
        styles.content
      }
    >
      <Text style={styles.title}>
        Upload Document
      </Text>

      {/* --------------------------------------- */}
      {/* Folder selector */}
      {/* --------------------------------------- */}

      <View style={styles.folderSection}>
        <Text style={styles.label}>
          Folder
        </Text>

        <TouchableOpacity
          style={styles.folderSelector}
          onPress={() =>
            setShowFolderSelector(
              !showFolderSelector
            )
          }
        >
          <Text style={styles.folderValue}>
            {selectedFolder}
          </Text>

          <Text
            style={styles.folderArrow}
          >
            {showFolderSelector
              ? "▲"
              : "▼"}
          </Text>
        </TouchableOpacity>

        {showFolderSelector && (
          <View
            style={styles.folderDropdown}
          >
            {folders.map((folder) => (
              <TouchableOpacity
                key={folder}
                style={[
                  styles.folderOption,
                  selectedFolder ===
                    folder &&
                    styles.selectedFolderOption,
                ]}
                onPress={() => {
                  setSelectedFolder(
                    folder
                  );
                  setShowFolderSelector(
                    false
                  );
                }}
              >
                <Text
                  style={
                    styles.folderOptionText
                  }
                >
                  {folder}
                </Text>

                {selectedFolder ===
                  folder && (
                  <Text
                    style={
                      styles.checkMark
                    }
                  >
                    ✓
                  </Text>
                )}
              </TouchableOpacity>
            ))}

            <TouchableOpacity
              style={
                styles.createFolderOption
              }
              onPress={() => {
                setShowCreateFolder(true);
              }}
            >
              <Text
                style={
                  styles.createFolderText
                }
              >
                + Create New Folder
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* ------------------------------------- */}
        {/* Create folder input */}
        {/* ------------------------------------- */}

        {showCreateFolder && (
          <View
            style={styles.createFolderBox}
          >
            <TextInput
              style={styles.input}
              placeholder="Enter folder name"
              placeholderTextColor={
                Colors.foreground
              }
              value={newFolderName}
              onChangeText={
                setNewFolderName
              }
              autoFocus
              autoCapitalize="words"
            />

            <View
              style={
                styles.createFolderButtons
              }
            >
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => {
                  setNewFolderName("");
                  setShowCreateFolder(
                    false
                  );
                }}
              >
                <Text
                  style={
                    styles.cancelButtonText
                  }
                >
                  Cancel
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.createButton}
                onPress={createFolder}
              >
                <Text
                  style={
                    styles.createButtonText
                  }
                >
                  Create
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>

      {/* --------------------------------------- */}
      {/* Select file */}
      {/* --------------------------------------- */}

      {!selectedFile && (
        <UploadButton
          title="Select File"
          onPress={pickDocument}
        />
      )}

      {/* --------------------------------------- */}
      {/* Selected file */}
      {/* --------------------------------------- */}

      {selectedFile && (
        <>
          <View style={styles.card}>
            <Text style={styles.label}>
              Folder
            </Text>

            <Text style={styles.value}>
              {selectedFolder}
            </Text>

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
                (selectedFile.size ?? 0) /
                1024
              ).toFixed(2)}{" "}
              KB
            </Text>

            <Text style={styles.label}>
              MIME Type
            </Text>

            <Text style={styles.value}>
              {selectedFile.mimeType ??
                "Unknown"}
            </Text>
          </View>

          <UploadButton
            title={`Upload to ${selectedFolder}`}
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

  folderSection: {
    gap: 8,
  },

  label: {
    color: Colors.primary,
    fontWeight: "600",
  },

  folderSelector: {
    minHeight: 50,
    paddingHorizontal: 16,
    borderRadius: 10,
    backgroundColor:
      Colors.sidebar,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  folderValue: {
    color: Colors.foreground,
    fontSize: 16,
    fontWeight: "500",
  },

  folderArrow: {
    color: Colors.foreground,
    fontSize: 14,
  },

  folderDropdown: {
    backgroundColor:
      Colors.sidebar,
    borderRadius: 10,
    overflow: "hidden",
  },

  folderOption: {
    minHeight: 48,
    paddingHorizontal: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  selectedFolderOption: {
    opacity: 0.7,
  },

  folderOptionText: {
    color: Colors.foreground,
    fontSize: 15,
  },

  checkMark: {
    color: Colors.primary,
    fontSize: 18,
    fontWeight: "700",
  },

  createFolderOption: {
    minHeight: 48,
    paddingHorizontal: 16,
    justifyContent: "center",
    borderTopWidth: 1,
    borderTopColor:
      Colors.background,
  },

  createFolderText: {
    color: Colors.primary,
    fontSize: 15,
    fontWeight: "600",
  },

  createFolderBox: {
    backgroundColor:
      Colors.sidebar,
    padding: 12,
    borderRadius: 10,
    gap: 12,
  },

  input: {
    minHeight: 45,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor:
      Colors.background,
    color: Colors.foreground,
    borderWidth: 1,
    borderColor:
      Colors.primary,
  },

  createFolderButtons: {
    flexDirection: "row",
    justifyContent: "flex-end",
    gap: 10,
  },

  cancelButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },

  cancelButtonText: {
    color: Colors.foreground,
  },

  createButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor:
      Colors.primary,
  },

  createButtonText: {
    color: Colors.background,
    fontWeight: "600",
  },

  card: {
    backgroundColor:
      Colors.sidebar,
    padding: 16,
    borderRadius: 10,
    gap: 8,
  },

  value: {
    color: Colors.foreground,
  },
});