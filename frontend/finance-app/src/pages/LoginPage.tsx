import {
  Box,
  Button,
  Flex,
  Heading,
  Alert,
  Stack,
  Field,
  Input,
} from "@chakra-ui/react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, type LoginCredentials } from "@/schemas/auth";
import useLogin from "@/hooks/useLogin";
import { Link, useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({ resolver: zodResolver(loginSchema) });

  const { mutate: login, isPending, error } = useLogin();

  const onSubmit = (data: LoginCredentials) =>
    login(data, {
      onSuccess: () => navigate("/dashboard"),
    });

  return (
    <Flex minH="100vh" align="center" justify="center">
      <Box p={8} rounded="lg" shadow="md" w="sm">
        <Heading mb={6} textAlign="center">
          Login
        </Heading>

        {error && (
          <Alert.Root status="error" variant="solid" mb="4">
            <Alert.Indicator />
            <Alert.Title>{(error as Error).message}</Alert.Title>
          </Alert.Root>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Stack gap="4">
            <Field.Root invalid={!!errors.username}>
              <Field.Label>Username</Field.Label>
              <Input placeholder="username" {...register("username")} />
              {errors.username && (
                <Field.ErrorText>{errors.username.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Field.Root invalid={!!errors.password}>
              <Field.Label>Password</Field.Label>
              <Input type="password" {...register("password")} />
              {errors.password && (
                <Field.ErrorText>{errors.password.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Button w="full" type="submit" loading={isPending}>
              Sign in
            </Button>
            <Box textAlign="center">
              <Link to="/register" color="teal.500">
                Create an account
              </Link>
            </Box>
          </Stack>
        </form>
      </Box>
    </Flex>
  );
}
