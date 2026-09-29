import { useMutation } from "@tanstack/react-query";
import { authService, type LoginResult } from "@/services/authClient";
import type { RegisterCredentials } from "@/schemas/auth";
import { useAuth } from "@/context/AuthContext";

export function useRegister() {
  const { login: loginContext } = useAuth();

  return useMutation<LoginResult, Error, RegisterCredentials>({
    mutationFn: authService.register,
    onSuccess: ({ token, user }) => loginContext(user, token),
  });
}
