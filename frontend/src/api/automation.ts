import { apiClient } from "@/api/client";

export type AutomationTriggerResponse = {
  status: string;
  event_type: string;
  event_id: string;
};

export async function triggerTicketCreatedAutomation(
  ticketId: string
): Promise<AutomationTriggerResponse> {
  const response = await apiClient.post<AutomationTriggerResponse>(
    `/automation/ticket-created/${ticketId}`
  );

  return response.data;
}

export async function triggerAiCompletedAutomation(
  ticketId: string
): Promise<AutomationTriggerResponse> {
  const response = await apiClient.post<AutomationTriggerResponse>(
    `/automation/ai-completed/${ticketId}`
  );

  return response.data;
}