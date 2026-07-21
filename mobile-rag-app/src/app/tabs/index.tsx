import { StyleSheet, Text, View } from "react-native";

import { Colors } from "@/theme";

export default function ChatScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Chat
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,

    justifyContent: "center",
    alignItems: "center",
  },

  title: {
    color: Colors.foreground,
    fontSize: 22,
    fontWeight: "700",
  },
});