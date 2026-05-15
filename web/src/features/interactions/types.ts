export type InteractionType = "call" | "email" | "meeting" | "note" | "task";

export type InteractionItem = {
  id: string;
  organization_id: string;
  user_id: string | null;
  deal_id: string | null;
  interaction_type: InteractionType;
  subject: string;
  description: string | null;
  happened_at: string;
  created_at: string;
};

export type InteractionCreate = {
  user_id: string | null;
  deal_id: string | null;
  interaction_type: InteractionType;
  subject: string;
  description: string | null;
  happened_at: string;
};

export type InteractionUpdate = Partial<InteractionCreate>;