import type { User } from "../types";

export type SessionState = {
  user: User | null;
  isReady: boolean;
};

export const initialSessionState: SessionState = {
  user: null,
  isReady: false
};
