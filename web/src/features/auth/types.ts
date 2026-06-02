export type AuthCredentials = {
  email: string;
  password: string;
};

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string;
  role: string | null;
  is_active: boolean;
};
