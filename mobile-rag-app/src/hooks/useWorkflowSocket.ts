import { useEffect, useState } from "react";
import { WorkflowSocket } from "@/services/websocket";
import type { WorkflowEvent } from "@/services/websocket";


export function useWorkflowSocket(
    workflowId?: string
) {

    const [event, setEvent] =
        useState<WorkflowEvent | null>(null);


    useEffect(() => {

        if (!workflowId) return;


        const socket =
            new WorkflowSocket(workflowId);


        socket.connect(
            (message) => {

                console.log(
                    "[Workflow Event]",
                    message
                );

                setEvent(message);

            }
        );


        return () => {

            socket.disconnect();

        };


    }, [workflowId]);


    return event;
}