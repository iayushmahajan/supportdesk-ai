import { apiClient } from "@/api/client";
import type {
  EmailTicketCreatePayload,
  Ticket,
  TicketCreatePayload,
  TicketDetail,
  TicketStatusUpdatePayload,
} from "@/types/ticket";

export async function createTicket(
  payload: TicketCreatePayload
): Promise<Ticket> {
  const response = await apiClient.post<Ticket>("/tickets", payload);
  return response.data;
}

export async function createTicketFromEmail(
  payload: EmailTicketCreatePayload
): Promise<TicketDetail> {
  const response = await apiClient.post<TicketDetail>(
    "/tickets/email-intake",
    payload
  );
  return response.data;
}

export async function getTickets(): Promise<Ticket[]> {
  const response = await apiClient.get<Ticket[]>("/tickets");
  return response.data;
}

export async function getTicketById(ticketId: string): Promise<TicketDetail> {
  const response = await apiClient.get<TicketDetail>(`/tickets/${ticketId}`);
  return response.data;
}

export async function updateTicketStatus(
  ticketId: string,
  payload: TicketStatusUpdatePayload
): Promise<Ticket> {
  const response = await apiClient.patch<Ticket>(
    `/tickets/${ticketId}/status`,
    payload
  );

  return response.data;
}

export async function processTicketWithAi(
  ticketId: string
): Promise<TicketDetail> {
  const response = await apiClient.post<TicketDetail>(
    `/tickets/${ticketId}/process-ai`
  );

  return response.data;
}

export async function reprocessTicketWithAi(
  ticketId: string
): Promise<TicketDetail> {
  const response = await apiClient.post<TicketDetail>(
    `/tickets/${ticketId}/reprocess-ai`
  );

  return response.data;
}