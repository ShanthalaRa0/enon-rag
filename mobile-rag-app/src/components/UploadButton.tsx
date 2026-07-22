import { Pressable, StyleSheet, Text } from "react-native";

import { Colors } from "@/theme";

interface UploadButtonProps {
  title: string;
  onPress: () => void;
  disabled?: boolean;
}

export default function UploadButton({
  title,
  onPress,
  disabled = false,
}: UploadButtonProps) {
  return (
    <Pressable
      style={[
        styles.button,
        disabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={disabled}
    >
      <Text style={styles.text}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: Colors.primary,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 10,
    alignItems: "center",
    width: "100%",
  },

  disabled: {
    opacity: 0.5,
  },

  text: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});