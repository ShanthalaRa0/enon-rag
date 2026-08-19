import React from "react";
import { ScrollView, StyleSheet, Text } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Colors } from "@/theme";

export default function TextViewer() {
  const { content, filename } = useLocalSearchParams<{
    content?: string;
    filename?: string;
  }>();

  let decodedContent = "";

  try {
    decodedContent = content
      ? decodeURIComponent(content)
      : "";
  } catch (error) {
    console.error("Failed to decode text content:", error);

    // If it wasn't URI encoded, use it directly
    decodedContent = content ?? "";
  }

  return (
    <ScrollView
      style={[
        styles.screen,
        { backgroundColor: Colors.background },
      ]}
      contentContainerStyle={styles.container}
    >
      {filename && (
        <Text
          style={[
            styles.filename,
            { color: Colors.foreground },
          ]}
        >
          {filename}
        </Text>
      )}

      <Text
        style={[
          styles.text,
          { color: Colors.foreground },
        ]}
      >
        {decodedContent}
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
  },

  container: {
    padding: 16,
  },

  filename: {
    fontSize: 20,
    fontWeight: "700",
    marginBottom: 16,
  },

  text: {
    fontSize: 15,
    lineHeight: 24,
    fontFamily: "monospace",
  },
});