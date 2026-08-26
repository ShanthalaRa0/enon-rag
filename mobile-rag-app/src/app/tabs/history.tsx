import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { Colors } from "@/theme";

import {
  useUpload,
  UploadHistoryItem,
} from "../../context/UploadContext";

export default function HistoryScreen() {
  const {
    uploadHistory,
  } = useUpload();

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={
        styles.content
      }
    >
      <Text style={styles.title}>
        Upload History
      </Text>

      {uploadHistory.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyText}>
            No uploads yet.
          </Text>
        </View>
      ) : (
        uploadHistory.map((item) => (
          <HistoryCard
            key={item.id}
            item={item}
          />
        ))
      )}
    </ScrollView>
  );
}

// ==================================================
// History Card
// ==================================================

function HistoryCard({
  item,
}: {
  item: UploadHistoryItem;
}) {
  return (
    <View style={styles.card}>

      {/* ------------------------------------------
          File name
          ------------------------------------------ */}

      <Text style={styles.filename}>
        {item.filename}
      </Text>

      {/* ------------------------------------------
          Status
          ------------------------------------------ */}

      <View style={styles.row}>
        <Text style={styles.label}>
          Status
        </Text>

        <Text
          style={[
            styles.status,

            item.status ===
              "RUNNING" &&
              styles.running,

            item.status ===
              "COMPLETED" &&
              styles.completed,

            item.status ===
              "FAILED" &&
              styles.failed,
          ]}
        >
          {item.status}
        </Text>
      </View>

      {/* ------------------------------------------
          Current stage
          ------------------------------------------ */}

      <View style={styles.row}>
        <Text style={styles.label}>
          Stage
        </Text>

        <Text style={styles.value}>
          {item.currentStage}
        </Text>
      </View>

      {/* ------------------------------------------
          Progress
          ------------------------------------------ */}

      <View style={styles.row}>
        <Text style={styles.label}>
          Progress
        </Text>

        <Text style={styles.value}>
          {item.progress}%
        </Text>
      </View>

      {/* ------------------------------------------
          Progress bar
          ------------------------------------------ */}

      <View
        style={
          styles.progressBackground
        }
      >
        <View
          style={[
            styles.progress,
            {
              width:
                `${Math.max(
                  0,
                  Math.min(
                    item.progress,
                    100
                  )
                )}%`,
            },
          ]}
        />
      </View>

      {/* ------------------------------------------
          Workflow ID
          ------------------------------------------ */}

      {item.workflowId && (
        <View style={styles.row}>
          <Text style={styles.label}>
            Workflow
          </Text>

          <Text
            style={styles.workflowId}
            numberOfLines={1}
          >
            {item.workflowId}
          </Text>
        </View>
      )}

      {/* ------------------------------------------
          Error
          ------------------------------------------ */}

      {item.error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>
            {item.error}
          </Text>
        </View>
      )}

      {/* ------------------------------------------
          Created time
          ------------------------------------------ */}

      <Text style={styles.date}>
        {formatDate(item.createdAt)}
      </Text>

      {/* ------------------------------------------
          Completed time
          ------------------------------------------ */}

      {item.completedAt && (
        <Text style={styles.date}>
          Completed:{" "}
          {formatDate(
            item.completedAt
          )}
        </Text>
      )}
    </View>
  );
}

// ==================================================
// Date formatter
// ==================================================

function formatDate(
  value: string
) {
  try {
    return new Date(
      value
    ).toLocaleString();
  } catch {
    return value;
  }
}

// ==================================================
// Styles
// ==================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor:
      Colors.background,
  },

  content: {
    padding: 20,
    gap: 16,
  },

  title: {
    fontSize: 24,
    fontWeight: "700",
    color: Colors.foreground,
  },

  emptyCard: {
    backgroundColor:
      Colors.sidebar,
    padding: 20,
    borderRadius: 10,
  },

  emptyText: {
    color: Colors.foreground,
    textAlign: "center",
  },

  card: {
    backgroundColor:
      Colors.sidebar,
    padding: 16,
    borderRadius: 12,
    gap: 10,
  },

  filename: {
    fontSize: 17,
    fontWeight: "700",
    color: Colors.foreground,
  },

  row: {
    flexDirection: "row",
    justifyContent:
      "space-between",
    alignItems: "center",
    gap: 10,
  },

  label: {
    color: Colors.primary,
    fontWeight: "600",
  },

  value: {
    color: Colors.foreground,
    flex: 1,
    textAlign: "right",
  },

  workflowId: {
    color: Colors.foreground,
    flex: 1,
    textAlign: "right",
    fontSize: 11,
  },

  status: {
    fontWeight: "700",
  },

  running: {
    color: Colors.primary,
  },

  completed: {
    color: "green",
  },

  failed: {
    color: "red",
  },

  progressBackground: {
    height: 8,
    backgroundColor:
      Colors.background,
    borderRadius: 4,
    overflow: "hidden",
  },

  progress: {
    height: "100%",
    backgroundColor:
      Colors.primary,
  },

  errorBox: {
    padding: 10,
    borderRadius: 8,
    backgroundColor:
      "rgba(255, 0, 0, 0.1)",
  },

  errorText: {
    color: "red",
  },

  date: {
    fontSize: 12,
    color: Colors.foreground,
    opacity: 0.6,
  },
});