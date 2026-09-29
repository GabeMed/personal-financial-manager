import { isAxiosError } from "axios";

/** Extracts FastAPI's `detail` message from an error, if there is one. */
export function getErrorMessage(err: unknown, fallback = "Something went wrong") {
  if (isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
  }
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}
