import { Colors } from "@/theme";
import { Text, View } from "react-native";

export default function WorkspaceScreen() {
  return (
    <View
      style={{
        flex: 1,
        backgroundColor: Colors.background,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text style={{ color: Colors.foreground }}>
        Workspace
      </Text>
    </View>
  );
}