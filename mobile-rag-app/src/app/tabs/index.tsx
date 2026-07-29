import React, { useRef, useState } from "react";
import { sendQuestion } from "@/services/chat";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Colors } from "@/theme";

type MessageRole = "user" | "assistant";

type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
};

export default function ChatScreen() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const flatListRef = useRef<FlatList<ChatMessage>>(null);

  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmedMessage,
    };

    // Immediately display user's message
    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    // Clear input
    setMessage("");

    setIsLoading(true);

    try {
      console.log("[CHAT] Sending question:", trimmedMessage);

      const response = await sendQuestion(trimmedMessage);

      console.log("[CHAT] Response:", response);

      const assistantMessage: ChatMessage = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content:
          response.length > 0
            ? response[0].text
            : "I couldn't find relevant information.",
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

    } catch (error) {
      console.error("[CHAT] Request failed:", error);

      const assistantMessage: ChatMessage = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content:
          "Sorry, I couldn't process your question. Please try again.",
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({
    item,
  }: {
    item: ChatMessage;
  }) => {
    const isUser = item.role === "user";

    return (
      <View
        style={[
          styles.messageRow,
          isUser
            ? styles.userMessageRow
            : styles.assistantMessageRow,
        ]}
      >
        {!isUser && (
          <View style={styles.assistantIcon}>
            <Ionicons
              name="sparkles"
              size={17}
              color="#111"
            />
          </View>
        )}

        <View
          style={[
            styles.messageContent,
            isUser
              ? styles.userMessageContent
              : styles.assistantMessageContent,
          ]}
        >
          <Text style={styles.messageText}>
            {item.content}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={
        Platform.OS === "ios"
          ? "padding"
          : "height"
      }
      keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          RAG Assistant
        </Text>

        <Pressable
          style={styles.headerButton}
          onPress={() => setMessages([])}
        >
          <Ionicons
            name="create-outline"
            size={22}
            color="#222"
          />
        </Pressable>
      </View>

      {/* Conversation */}
      <View style={styles.conversation}>
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <View style={styles.logoContainer}>
              <Ionicons
                name="sparkles"
                size={30}
                color="#111"
              />
            </View>

            <Text style={styles.emptyTitle}>
              How can I help?
            </Text>

            <Text style={styles.emptySubtitle}>
              Ask questions about your uploaded documents.
            </Text>
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={renderMessage}
            contentContainerStyle={
              styles.messagesContent
            }
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
            onContentSizeChange={() =>
              flatListRef.current?.scrollToEnd({
                animated: true,
              })
            }
          />
        )}
      </View>

      {/* Bottom Input */}
      <View style={styles.inputArea}>
        <View style={styles.inputWrapper}>
          <TextInput
            style={styles.input}
            value={message}
            onChangeText={setMessage}
            placeholder="Message RAG Assistant"
            placeholderTextColor="#8a8a8a"
            maxLength={4000}
            returnKeyType="send"
            onSubmitEditing={sendMessage}
          />

          <Pressable
            style={[
              styles.sendButton,
              (!message.trim() || isLoading) &&
                styles.sendButtonDisabled,
            ]}
            onPress={sendMessage}
            disabled={!message.trim() || isLoading}
          >
            <Ionicons
              name={isLoading ? "hourglass-outline" : "arrow-up"}
              size={19}
              color={
                message.trim() && !isLoading
                  ? "#fff"
                  : "#aaa"
              }
            />
          </Pressable>
        </View>

        <Text style={styles.disclaimer}>
          RAG Assistant can make mistakes. Check important information.
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },

  /* ---------------- Header ---------------- */

  header: {
    height: 56,
    paddingHorizontal: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },

  headerTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: Colors.foreground,
  },

  headerButton: {
    width: 40,
    height: 40,
    alignItems: "center",
    justifyContent: "center",
  },

  /* ---------------- Conversation ---------------- */

  conversation: {
    flex: 1,
  },

  messagesContent: {
    paddingTop: 20,
    paddingBottom: 24,
  },

  messageRow: {
    width: "100%",
    paddingHorizontal: 16,
    paddingVertical: 14,
    flexDirection: "row",
  },

  userMessageRow: {
    justifyContent: "flex-end",
  },

  assistantMessageRow: {
    justifyContent: "flex-start",
    backgroundColor: Colors.background,
  },

  assistantIcon: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: "#f0f0f0",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 10,
    marginTop: 1,
  },

  messageContent: {
    maxWidth: "82%",
  },

  userMessageContent: {
    backgroundColor: Colors.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 11,
  },

  assistantMessageContent: {
    flex: 1,
    paddingRight: 8,
  },

  messageText: {
    fontSize: 16,
    lineHeight: 24,
    color: Colors.foreground,
  },

  /* ---------------- Empty State ---------------- */

  emptyState: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 32,
    paddingBottom: 60,
  },

  logoContainer: {
    width: 58,
    height: 58,
    borderRadius: 29,
    backgroundColor: "#f1f1f1",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 18,
  },

  emptyTitle: {
    fontSize: 25,
    fontWeight: "600",
    color: "#222",
    marginBottom: 8,
  },

  emptySubtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: "#777",
    textAlign: "center",
  },

  /* ---------------- Input ---------------- */

  inputArea: {
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: Platform.OS === "ios" ? 8 : 10,
    backgroundColor: "#302e2e",
  },

  inputWrapper: {
    minHeight: 50,
    maxHeight: 140,
    borderWidth: 1,
    borderColor: "#d9d9d9",
    borderRadius: 25,
    backgroundColor: "#fff",
    flexDirection: "row",
    alignItems: "flex-end",
    paddingLeft: 17,
    paddingRight: 6,
    paddingVertical: 5,

    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },

  input: {
    flex: 1,
    fontSize: 16,
    lineHeight: 22,
    color: "#000000",
    paddingTop: 8,
    paddingBottom: 8,
    maxHeight: 120,
  },

  sendButton: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: "#111",
    alignItems: "center",
    justifyContent: "center",
  },

  sendButtonDisabled: {
    backgroundColor: "#e5e5e5",
  },

  disclaimer: {
    textAlign: "center",
    fontSize: 11,
    color: "#999",
    marginTop: 7,
  },
});
