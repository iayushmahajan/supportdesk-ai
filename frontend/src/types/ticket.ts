export type TicketStatus =
  | "open"
  | "in_progress"
  | "waiting_customer"
  | "resolved"
  | "closed";

export type TicketPriority =
  | "unassigned"
  | "low"
  | "medium"
  | "high"
  | "urgent";

export type TicketCategory =
  | "unclassified"
  | "technical"
  | "billing"
  | "account"
  | "document"
  | "general";

export type TicketSource = "form" | "email";

export type MessageSenderType = "requester" | "agent" | "system";

export type AgentRunStatus = "pending" | "running" | "completed" | "failed";

export type AutomationEventStatus = "pending" | "sent" | "failed";

export type TicketCreatePayload = {
  requester_name: string;
  requester_email: string;
  subject: string;
  description: string;
  source: TicketSource;
};

export type EmailTicketCreatePayload = {
  from_name: string;
  from_email: string;
  email_subject: string;
  email_body: string;
};

export type TicketStatusUpdatePayload = {
  status: TicketStatus;
};

export type TicketMessage = {
  id: string;
  sender_type: MessageSenderType;
  sender_name: string | null;
  sender_email: string | null;
  body: string;
  created_at: string;
};

export type AgentRun = {
  id: string;
  agent_name: string;
  execution_order: number;
  status: AgentRunStatus;
  input_json: Record<string, unknown> | null;
  output_json: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
};

export type GeneratedResponse = {
  id: string;
  response_text: string;
  tone: string;
  is_approved: boolean;
  created_at: string;
};

export type AutomationEvent = {
  id: string;
  event_type: string;
  status: AutomationEventStatus;
  provider: string;
  payload_json: Record<string, unknown> | null;
  response_json: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type TicketAttachment = {
  id: string;
  file_name: string;
  content_type: string | null;
  file_size_bytes: number | null;
  storage_path: string | null;
  created_at: string;
};

export type Ticket = {
  id: string;

  requester_name: string;
  requester_email: string;

  subject: string;
  description: string;
  source: TicketSource;

  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;

  suggested_department: string | null;
  internal_summary: string | null;

  created_at: string;
  updated_at: string;
};

export type TicketDetail = Ticket & {
  messages: TicketMessage[];
  agent_runs: AgentRun[];
  generated_responses: GeneratedResponse[];
  automation_events: AutomationEvent[];
  attachments: TicketAttachment[];
};