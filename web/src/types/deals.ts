export type DealStage = "new" | "negotiation" | "approved" | "rejected" | "closed";

export type DealItem = {
  id: string;
  organization_id: string;
  owner_id: string | null;
  title: string;
  stage: DealStage;
  amount: string | null;
  currency: string;
  expected_close_date: string | null;
  closed_at: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type DealCreate = {
  owner_id: string | null;
  title: string;
  stage: DealStage;
  amount: number | null;
  currency: string;
  expected_close_date: string | null;
  description: string | null;
};

export type DealUpdate = Partial<DealCreate> & {
  closed_at?: string | null;
};