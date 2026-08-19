import { Colors } from "@/theme";
import React, { useCallback, useState,} from "react";
import {
  ActivityIndicator,
  FlatList,
  Linking,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useFocusEffect } from "expo-router";
import { useRouter } from "expo-router";

import { API_URL } from "@/config/api";

type WorkspaceItem = {
  name: string;
  type: "folder" | "file";
  children?: WorkspaceItem[];
};

type WorkspaceResponse = {
  message: string;
  results: WorkspaceItem;
};

export default function WorkspaceScreen() {
  const [workspace, setWorkspace] = useState<WorkspaceItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWorkspace = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/workspace`);

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data: WorkspaceResponse = await response.json();

      setWorkspace(data.results);
    } catch (error) {
      console.error("Failed to load workspace:", error);
      setError("Unable to load workspace.");
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadWorkspace();
    }, [])
  );

  if (loading) {
    return (
      <View style={[styles.center, { backgroundColor: Colors.background }]}>
        <ActivityIndicator />
        <Text style={{ color: Colors.foreground }}>
          Loading workspace...
        </Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.center, { backgroundColor: Colors.background }]}>
        <Text style={{ color: Colors.foreground }}>
          {error}
        </Text>

        <TouchableOpacity
          style={styles.retryButton}
          onPress={loadWorkspace}
        >
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!workspace) {
    return (
      <View style={[styles.center, { backgroundColor: Colors.background }]}>
        <Text style={{ color: Colors.foreground }}>
          No workspace data found.
        </Text>
      </View>
    );
  }

  return (
    <View
      style={[
        styles.container,
        { backgroundColor: Colors.background },
      ]}
    >
      <Text
        style={[
          styles.title,
          { color: Colors.foreground },
        ]}
      >
        Workspace
      </Text>

      <FlatList
        data={workspace.children ?? []}
        keyExtractor={(item, index) =>
          `${item.name}-${index}`
        }
        renderItem={({ item }) => (
          <WorkspaceRow item={item} />
        )}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

function WorkspaceRow({ item }: { item: WorkspaceItem }) {
  const [expanded, setExpanded] = useState(false);

  const router = useRouter();

  const isFolder = item.type === "folder";

  const handlePress = async () => {
    if (isFolder) {
      setExpanded((previous) => !previous);
      return;
    }

    const extension = item.name
      .split(".")
      .pop()
      ?.toLowerCase() ?? "";
    
    const fileUrl = `${API_URL}/workspace/file/${encodeURIComponent(item.name)}`;
    try {
      if (
        [
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
        ].includes(extension)
      ) {
        // Open the original PDF
        const supported = await Linking.canOpenURL(fileUrl);

        if (supported) {
          await Linking.openURL(fileUrl);
        } else {
          console.error("Cannot open file:", fileUrl);
        }

        return;
      }

      if (extension === "txt") {
        const response = await fetch(
          `${API_URL}/workspace/file/${encodeURIComponent(item.name)}`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load text file: ${response.status}`
          );
        }

        const text = await response.text();

        router.push({
          pathname: "/text-viewer",
          params: {
            content: encodeURIComponent(text),
          },
        });

        return;
      }

      console.log("Unsupported file type:", extension);

    } catch (error) {
      console.error("Failed to open file:", error);
    }
  };

  return (
    <View>
      <TouchableOpacity
        style={styles.row}
        onPress={handlePress}
        activeOpacity={0.7}
      >
        <Text style={styles.icon}>
          {isFolder
            ? expanded
              ? "📂"
              : "📁"
            : "📄"}
        </Text>

        <Text
          style={[
            styles.fileName,
            { color: Colors.foreground },
          ]}
          numberOfLines={1}
        >
          {item.name}
        </Text>

        {isFolder && (
          <Text
            style={[
              styles.arrow,
              { color: Colors.foreground },
            ]}
          >
            {expanded ? "⌄" : "›"}
          </Text>
        )}
      </TouchableOpacity>

      {isFolder && expanded && item.children && (
        <View style={styles.children}>
          {item.children.map((child, index) => (
            <WorkspaceRow
              key={`${child.name}-${index}`}
              item={child}
            />
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 20,
  },

  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },

  title: {
    fontSize: 28,
    fontWeight: "700",
    marginBottom: 20,
  },

  row: {
    minHeight: 48,
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
  },

  icon: {
    fontSize: 22,
    width: 38,
  },

  fileName: {
    flex: 1,
    fontSize: 16,
  },

  arrow: {
    fontSize: 24,
    width: 30,
    textAlign: "center",
  },

  children: {
    marginLeft: 24,
  },

  retryButton: {
    marginTop: 16,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: "#007AFF",
  },

  retryText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "600",
  },
});